# SPDX-FileCopyrightText: 2024 CERN
#
# SPDX-License-Identifier: BSD-4-Clause

import copy
import functools
import itertools
import logging
import math
import pathlib
import re
import tempfile
from typing import Callable, Optional

import gmsh
import numpy as np
import numpy.typing as npt
from roxieapi.cadata.CableDatabase import CableDatabase
from roxieapi.commons.types import BlockTopology, Coil3DGeometry, WedgeSurface
from roxieapi.input.builder import RoxieInputBuilder
from roxieapi.output.parser import RoxieOutputParser
from scipy.sparse import csr_array
from scipy.sparse.csgraph import breadth_first_order
from tqdm.autonotebook import tqdm

from roxieinterfaces import __version__ as roxie_interfaces_version
from roxieinterfaces.geom.bsplines import BSpline_3D
from roxieinterfaces.geom.math_tools import (
    add_insulation_thickness,
    get_intersection_line_cylinder,
    normalize_vectors,
)
from roxieinterfaces.mesh.stepplot import StepPlotter

STEP_PROD_REGEXP = r"'Open CASCADE STEP translator [\d\.]+ [\d\.]+'"

logger = logging.getLogger(__name__)


def gmsh_cleanup(main_func):
    @functools.wraps(main_func)
    def wrapper(*args, **kwargs) -> None:
        obj: StepGeneratorBase = args[0]
        try:
            main_func(*args, **kwargs)
        finally:
            obj.model_name = None
            obj.model_color = None
            gmsh.clear()

    return wrapper


def apply_pre_funcs(main_func):
    @functools.wraps(main_func)
    def wrapper(*args, **kwargs) -> None:
        obj: StepGeneratorBase = args[0]
        for pre_func in obj._wrapper_pre_funcs:
            pre_func(*args, **kwargs)
        main_func(*args, **kwargs)

    return wrapper


def apply_post_funcs(main_func):
    @functools.wraps(main_func)
    def wrapper(*args, **kwargs) -> None:
        obj: StepGeneratorBase = args[0]
        main_func(*args, **kwargs)
        for post_func in obj._wrapper_post_funcs:
            post_func(*args, **kwargs)

    return wrapper


def optional_features(main_func):  # -> Callable[[], None]:
    """Decorator applying optional features for generation of blocks. Controlled by flags from StepGenerator
    * Apply symmetry
    * Write step file
    * write vtk file
    * plot output
    """

    @gmsh_cleanup
    @apply_post_funcs
    @apply_pre_funcs
    @functools.wraps(main_func)
    def wrapper(*args, **kwargs) -> None:
        return main_func(*args, **kwargs)

    return wrapper


class StepGeneratorBase:
    """Base class for step generators

    (shared functions between classic Step generator and Step generator based only on coils)
    """

    def __init__(self, n_straight=1) -> None:
        self.logger = logging.getLogger("StepGeneratorBase")
        self.n_straight = n_straight

        self.apply_sym: Optional[tuple[int, int, int]] = None
        self.step_plotter: Optional[StepPlotter] = None

        self._ins_r: Optional[dict[int, float]] = None
        self._ins_phi: Optional[dict[int, float]] = None
        self._origin_blocks: Optional[dict[int, int]] = None

        self.model_name: Optional[str] = None
        self.model_color: Optional[list[int]] = None
        self.output_step_folder: Optional[pathlib.Path] = None
        self.output_vtk_folder: Optional[pathlib.Path] = None

        self._conductor_orders: list[list[int]] = []
        self._conductor_order_dict: dict[int, tuple[int, int]]
        self._prepend_continuity_order: bool = False

        self.mesh_size = 100.0
        # initialize gmsh
        if not gmsh.isInitialized():
            gmsh.initialize()
        gmsh.option.setString("Geometry.OCCTargetUnit", "MM")
        gmsh.option.setNumber("General.Verbosity", 2)

        self._wrapper_pre_funcs: list[Callable[..., None]] = []
        self._wrapper_post_funcs: list[Callable[..., None]] = []

        def _add_model_name(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.model_name:
                gmsh.model.add(obj.model_name)

        def _write_step(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.output_step_folder and obj.model_name:
                step_name = str(obj.output_step_folder / (obj.model_name + ".step"))
                gmsh.option.setString(
                    "Geometry.OCCSTEPDescription",
                    f"Geometry generated with roxieinterfaces, version {roxie_interfaces_version}",
                )
                gmsh.option.setString("Geometry.OCCSTEPModelName", obj.model_name)
                gmsh.option.setString("Geometry.OCCSTEPAuthor", f"roxieinterfaces {roxie_interfaces_version}")
                gmsh.option.setString("Geometry.OCCSTEPOrganization", "CERN")
                gmsh.option.setString("Geometry.OCCSTEPPreprocessorVersion", "Gmsh")
                gmsh.option.setString("Geometry.OCCSTEPOriginatingSystem", "-")
                gmsh.option.setString("Geometry.OCCSTEPAuthorization", "")
                gmsh.option.setString("Geometry.OCCSTEPDescription", obj.model_name)

                # MB this does not change the name of the model when imported
                # TODO: figure out how to rename "product" name inside step file
                # dim3_tags = [el[1] for el in gmsh.model.occ.getEntities(dim=3)]
                # gmsh.model.geo.addPhysicalGroup (3,dim3_tags,name=obj.model_name)
                # gmsh.model.occ.synchronize()
                with tempfile.NamedTemporaryFile(suffix=".step", delete=True, dir=obj.output_step_folder) as tmp_file:
                    gmsh.write(tmp_file.name)
                    with open(tmp_file.name) as fr:
                        result = re.sub(
                            STEP_PROD_REGEXP, f"'{obj.model_name}'", fr.read(), count=0, flags=re.MULTILINE
                        )
                    with open(step_name, "w") as fw:
                        fw.write(result)

        def _write_vtk(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.output_vtk_folder and obj.model_name:
                vtk_name = str(obj.output_vtk_folder / (obj.model_name + ".vtk"))
                gmsh.write(vtk_name)

        def _apply_gmsh_color(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.model_color:
                gmsh.model.setColor(gmsh.model.getEntities(dim=3), *obj.model_color, recursive=True)

        def _plot_output(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.step_plotter:
                obj.step_plotter.plot_current_gmsh_model(obj.model_color)

        def _apply_symmetry(*args, **kwargs) -> None:
            obj: StepGeneratorBase = args[0]
            if obj.apply_sym:
                x, y, z = obj.apply_sym
                if x:
                    obj._apply_symmetry(1, 0, 0)
                if y:
                    obj._apply_symmetry(0, 1, 0)
                if z:
                    obj._apply_symmetry(0, 0, 1)

        self._wrapper_pre_funcs.append(_add_model_name)

        self._wrapper_post_funcs.append(_apply_symmetry)
        self._wrapper_post_funcs.append(_apply_gmsh_color)
        self._wrapper_post_funcs.append(_write_step)
        self._wrapper_post_funcs.append(_write_vtk)
        self._wrapper_post_funcs.append(_plot_output)

    def set_cable_parameters(self, topologies: dict[int, BlockTopology]):
        self._ins_r = {}
        self._ins_phi = {}
        self._origin_blocks = {}
        for row, bt in topologies.items():
            self._ins_r[row] = bt.ins_radial
            self._ins_phi[row] = bt.ins_azimuthal
            self._origin_blocks[row] = bt.block_orig

    def set_conductor_insulation_cadata(self, data_path: pathlib.Path, cadata_path: pathlib.Path):
        """Set conduction insulation values from cadata file.
        Deprecated. Insulation data is now stored in xml files. Use set_cable_parameters instead
        """
        cabledb = CableDatabase.read_cadata(str(cadata_path))
        datafile = RoxieInputBuilder.from_datafile(data_path)
        # load cablenames
        self._ins_r = {}
        self._ins_phi = {}
        for _, row in datafile.block.iterrows():
            insul = cabledb.get_insul_definition(row.condname)
            self._ins_r[row.no] = insul.thickness
            self._ins_phi[row.no] = insul.width

    def set_conductor_insualation(self, ins_r: float, ins_phi: float):
        """Set conductor insulation manually.
        Deprecated. Insulation data is now stored in xml files. Use set_cable_parameters instead
        """
        """Add insulation to conductor geometry
        :param ins_r:
            The thickness of the insulation in r direction.
        :type ins_r: float

        :param ins_phi:
            The thickness of the insulation in phi direction.
        :type ins_phi: float
        """
        self._ins_r = {0: ins_r}
        self._ins_phi = {0: ins_phi}

    def _get_ins_r(self, block_nr: int) -> float:
        if self._ins_r is None:
            raise ValueError("Insulation thickness not set")
        if 0 in self._ins_r:
            return self._ins_r[0]
        if block_nr not in self._ins_r:
            raise ValueError(f"No insulation thickness for block {block_nr}")
        return self._ins_r[block_nr]

    def _get_ins_phi(self, block_nr: int) -> float:
        if self._ins_phi is None:
            raise ValueError("Insulation width not set")
        if 0 in self._ins_phi:
            return self._ins_phi[0]
        if block_nr not in self._ins_phi:
            raise ValueError(f"No insulation width for block {block_nr}")
        return self._ins_phi[block_nr]

    def set_generate_step(self, output_folder: pathlib.Path):
        self.output_step_folder = output_folder

    def set_generate_vtk(self, output_folder: pathlib.Path):
        self.output_vtk_folder = output_folder

    def set_model_name(self, name: str):
        self.model_name = name

    def set_apply_symmetry(self, apply_sym_x: bool, apply_sym_y: bool, apply_sym_z: bool):
        self.apply_sym = (1 if apply_sym_x else 0, 1 if apply_sym_y else 0, 1 if apply_sym_z else 0)

    def set_step_plotter(self, plotter: StepPlotter):
        self.step_plotter = plotter

    def _apply_symmetry(self, sym_x: int = 0, sym_y: int = 0, sym_z: int = 0):
        ent_3d = gmsh.model.getEntities(3)
        solid_cpy = gmsh.model.occ.copy(ent_3d)
        gmsh.model.occ.synchronize()
        ent_3d = gmsh.model.getEntities(3)
        gmsh.model.occ.mirror(solid_cpy, sym_x, sym_y, sym_z, 0)
        gmsh.model.occ.synchronize()
        gmsh.model.occ.fuse([ent_3d[0]], [ent_3d[1]])
        gmsh.model.occ.synchronize()

    @optional_features
    def _create_coil_geometry(self, coil: Coil3DGeometry, add_insulation: bool = False) -> None:
        """
        Generate the geometry of a coil.

        :param coil: The 3D geometry of the coil.
        :type coil: Coil3DGeometry
        :param add_insulation: Add insulation thickness to coil geometry
        """
        if add_insulation:
            if not coil.geometry.elements:
                raise ValueError("The given coil is missing its element (connectivity) information")
            nodes = add_insulation_thickness(
                coil.geometry.nodes,
                coil.geometry.elements,
                self._get_ins_r(coil.block_id),
                self._get_ins_phi(coil.block_id),
            )
        else:
            nodes = coil.geometry.nodes

        self._make_wedge(nodes[::4, :], nodes[1::4, :], nodes[3::4, :], nodes[2::4, :])

    def get_coil_order_prefix(self, coil_nr: int) -> str:
        if self._prepend_continuity_order and coil_nr in self._conductor_order_dict:
            oidx, cidx = self._conductor_order_dict[coil_nr]
            return f"grp_{oidx:02d}_order_{cidx:03d}_"
        return ""

    def get_coil_geom(self, coil: Coil3DGeometry, add_insualation: bool = False) -> None:
        if not self.model_color:
            self.model_color = [0xE1, 0x00, 0x00]  # Default color red
        if not self.model_name:
            prefix = self.get_coil_order_prefix(coil.nr)
            self.set_model_name(f"{prefix}coil_{coil.nr:03d}")
        self._create_coil_geometry(coil, add_insualation)

    def get_all_coil_geoms(self, coils: dict[int, Coil3DGeometry], add_insulation: bool = False) -> None:
        """
        Generate the geometry of all coils.

        :param coils: The 3D geometry of the coils.
        :type coils: dict[int, Coil3DGeometry]

        :return: None
        """
        for idx, coil in tqdm(coils.items(), desc="Generating coil geometries"):
            self.logger.debug(f"Generating coil geometry for coil idx {idx}")
            prefix = self.get_coil_order_prefix(idx)
            self.set_model_name(f"{prefix}coil_{idx:03d}")
            self.get_coil_geom(coil, add_insulation)

    def get_zerogap_aligned_coil_geoms(
        self, coils: dict[int, Coil3DGeometry], coil_list: list[int], add_insulation: bool = True
    ) -> None:
        node_list = []
        for c in coil_list:
            coil = coils[c]
            if add_insulation:
                nodes = add_insulation_thickness(
                    coil.geometry.nodes,
                    coil.geometry.elements,
                    self._get_ins_r(coil.block_id),
                    self._get_ins_phi(coil.block_id),
                )
            else:
                nodes = coil.geometry.nodes
            node_list.append((c, nodes))

    def get_zerogap_aligned_coil_geoms_for_block(
        self, coils: dict[int, Coil3DGeometry], coil_block: BlockTopology, add_insulation: bool = True
    ) -> None:
        self.get_zerogap_aligned_coil_geoms(
            coils, list(range(coil_block.first_conductor, coil_block.last_conductor + 1)), add_insulation
        )

    def _make_wedge(
        self,
        points_front_bottom: npt.NDArray[np.float64],
        points_front_top: npt.NDArray[np.float64],
        points_back_bottom: npt.NDArray[np.float64],
        points_back_top: npt.NDArray[np.float64],
    ) -> list[tuple[int, int]]:
        targ_h = self.mesh_size

        # we extract the 'curvy' part
        p_llc = points_front_bottom[self.n_straight :, :]
        p_lrc = points_front_top[self.n_straight :, :]
        p_ulc = points_back_bottom[self.n_straight :, :]
        p_urc = points_back_top[self.n_straight :, :]

        # the number of points
        n_llc = p_llc.shape[0]
        n_lrc = p_lrc.shape[0]
        n_ulc = p_ulc.shape[0]
        n_urc = p_urc.shape[0]

        # we make a parameter vector
        t_llc = np.linspace(0.0, 1.0, n_llc)
        t_lrc = np.linspace(0.0, 1.0, n_lrc)
        t_ulc = np.linspace(0.0, 1.0, n_ulc)
        t_urc = np.linspace(0.0, 1.0, n_urc)

        bspline_llc = BSpline_3D()
        bspline_lrc = BSpline_3D()
        bspline_ulc = BSpline_3D()
        bspline_urc = BSpline_3D()

        bspline_llc.fit_to_points(t_llc, p_llc)
        bspline_lrc.fit_to_points(t_lrc, p_lrc)
        bspline_ulc.fit_to_points(t_ulc, p_ulc)
        bspline_urc.fit_to_points(t_urc, p_urc)

        # get the spline degrees
        k_llc = bspline_llc.degree
        k_ulc = bspline_ulc.degree
        k_lrc = bspline_lrc.degree
        k_urc = bspline_urc.degree

        # Define the B-Spline curves for gmsh
        points_list_llc = []
        points_list_lrc = []
        points_list_ulc = []
        points_list_urc = []

        for _, cpt in enumerate(bspline_llc.get_control_points()):
            points_list_llc.append(gmsh.model.occ.addPoint(cpt[0], cpt[1], cpt[2], targ_h))

        for _, cpt in enumerate(bspline_lrc.get_control_points()):
            points_list_lrc.append(gmsh.model.occ.addPoint(cpt[0], cpt[1], cpt[2], targ_h))

        for _, cpt in enumerate(bspline_ulc.get_control_points()):
            points_list_ulc.append(gmsh.model.occ.addPoint(cpt[0], cpt[1], cpt[2], targ_h))

        for _, cpt in enumerate(bspline_urc.get_control_points()):
            points_list_urc.append(gmsh.model.occ.addPoint(cpt[0], cpt[1], cpt[2], targ_h))

        multiplicities_llc = np.ones((len(bspline_llc.knots[k_llc:-k_llc]),))
        multiplicities_llc[0] = k_llc + 1
        multiplicities_llc[-1] = k_llc + 1

        multiplicities_ulc = np.ones((len(bspline_ulc.knots[k_ulc:-k_ulc]),))
        multiplicities_ulc[0] = k_ulc + 1
        multiplicities_ulc[-1] = k_ulc + 1

        multiplicities_urc = np.ones((len(bspline_urc.knots[k_urc:-k_urc]),))
        multiplicities_urc[0] = k_urc + 1
        multiplicities_urc[-1] = k_urc + 1

        multiplicities_lrc = np.ones((len(bspline_lrc.knots[k_lrc:-k_lrc]),))
        multiplicities_lrc[0] = k_lrc + 1
        multiplicities_lrc[-1] = k_lrc + 1

        # the splines for the four corners
        C_llc = gmsh.model.occ.addBSpline(
            points_list_llc,
            degree=k_llc,
            knots=bspline_llc.knots[k_llc:-k_llc],
            multiplicities=multiplicities_llc,
        )

        C_lrc = gmsh.model.occ.addBSpline(
            points_list_lrc,
            degree=k_lrc,
            knots=bspline_lrc.knots[k_lrc:-k_lrc],
            multiplicities=multiplicities_lrc,
        )

        C_ulc = gmsh.model.occ.addBSpline(
            points_list_ulc,
            degree=k_ulc,
            knots=bspline_ulc.knots[k_ulc:-k_ulc],
            multiplicities=multiplicities_ulc,
        )

        C_urc = gmsh.model.occ.addBSpline(
            points_list_urc,
            degree=k_urc,
            knots=bspline_urc.knots[k_urc:-k_urc],
            multiplicities=multiplicities_urc,
        )

        # the splines for the cable ends
        C0_west = gmsh.model.occ.addBSpline([points_list_ulc[0], points_list_llc[0]], degree=1)
        C0_east = gmsh.model.occ.addBSpline([points_list_urc[0], points_list_lrc[0]], degree=1)

        C0_south = gmsh.model.occ.addBSpline([points_list_lrc[0], points_list_llc[0]], degree=1)
        C0_north = gmsh.model.occ.addBSpline([points_list_urc[0], points_list_ulc[0]], degree=1)

        C1_west = gmsh.model.occ.addBSpline([points_list_llc[-1], points_list_ulc[-1]], degree=1)
        C1_east = gmsh.model.occ.addBSpline([points_list_lrc[-1], points_list_urc[-1]], degree=1)

        C1_south = gmsh.model.occ.addBSpline([points_list_llc[-1], points_list_lrc[-1]], degree=1)
        C1_north = gmsh.model.occ.addBSpline([points_list_ulc[-1], points_list_urc[-1]], degree=1)

        # Create a BSpline surface filling the six sides of the cable:
        Side1 = gmsh.model.occ.addWire([C0_west, C_llc, C1_west, C_ulc])
        Side2 = gmsh.model.occ.addWire([C0_east, C_lrc, C1_east, C_urc])

        Side3 = gmsh.model.occ.addWire([C0_north, C_ulc, C1_north, C_urc])
        Side4 = gmsh.model.occ.addWire([C0_south, C_llc, C1_south, C_lrc])

        Side5 = gmsh.model.occ.addWire([C0_south, C0_east, C0_north, C0_west])
        Side6 = gmsh.model.occ.addWire([C1_south, C1_east, C1_north, C1_west])

        s1 = gmsh.model.occ.addBSplineFilling(Side1, type="Stretch")
        s2 = gmsh.model.occ.addBSplineFilling(Side2, type="Stretch")
        s3 = gmsh.model.occ.addBSplineFilling(Side3, type="Stretch")
        s4 = gmsh.model.occ.addBSplineFilling(Side4, type="Stretch")
        s5 = gmsh.model.occ.addBSplineFilling(Side5, type="Stretch")
        s6 = gmsh.model.occ.addBSplineFilling(Side6, type="Stretch")

        # make a solid
        sloop = gmsh.model.occ.addSurfaceLoop([s1, s2, s3, s4, s5, s6])

        vol = gmsh.model.occ.addVolume([sloop])

        # now add the straight section
        pp1 = gmsh.model.occ.addPoint(
            points_front_bottom[0, 0],
            points_front_bottom[0, 1],
            points_front_bottom[0, 2],
            targ_h,
        )

        pp2 = gmsh.model.occ.addPoint(
            points_front_top[0, 0],
            points_front_top[0, 1],
            points_front_top[0, 2],
            targ_h,
        )

        pp3 = gmsh.model.occ.addPoint(points_back_top[0, 0], points_back_top[0, 1], points_back_top[0, 2], targ_h)

        pp4 = gmsh.model.occ.addPoint(
            points_back_bottom[0, 0],
            points_back_bottom[0, 1],
            points_back_bottom[0, 2],
            targ_h,
        )

        l1 = gmsh.model.occ.addLine(pp1, pp2)
        l2 = gmsh.model.occ.addLine(pp2, pp3)
        l3 = gmsh.model.occ.addLine(pp3, pp4)
        l4 = gmsh.model.occ.addLine(pp4, pp1)

        l5 = gmsh.model.occ.addLine(pp1, points_list_llc[0])
        l6 = gmsh.model.occ.addLine(pp2, points_list_lrc[0])
        l7 = gmsh.model.occ.addLine(pp3, points_list_urc[0])
        l8 = gmsh.model.occ.addLine(pp4, points_list_ulc[0])

        # the sides of the straight section
        c1 = gmsh.model.occ.addCurveLoop([l1, l2, l3, l4])
        ss1 = gmsh.model.occ.addSurfaceFilling(c1)

        c2 = gmsh.model.occ.addCurveLoop([l1, l6, C0_south, -l5])
        ss2 = gmsh.model.occ.addSurfaceFilling(c2)

        c3 = gmsh.model.occ.addCurveLoop([l2, l7, -C0_east, -l6])
        ss3 = gmsh.model.occ.addSurfaceFilling(c3)

        c4 = gmsh.model.occ.addCurveLoop([l3, l8, -C0_north, -l7])
        ss4 = gmsh.model.occ.addSurfaceFilling(c4)

        c5 = gmsh.model.occ.addCurveLoop([l4, l5, C0_west, -l8])
        ss5 = gmsh.model.occ.addSurfaceFilling(c5)

        # make a solid
        sloop_s = gmsh.model.occ.addSurfaceLoop([ss1, ss2, ss3, ss4, ss5, s5])

        vol_s = gmsh.model.occ.addVolume([sloop_s])
        result_tags, _ = gmsh.model.occ.fuse([(3, vol)], [(3, vol_s)])
        gmsh.model.occ.synchronize()

        # clean up
        ent_2d = gmsh.model.getEntities(2)
        gmsh.model.occ.remove(ent_2d)
        ent_1d = gmsh.model.getEntities(1)
        gmsh.model.occ.remove(ent_1d)
        ent_0d = gmsh.model.getEntities(0)
        gmsh.model.occ.remove(ent_0d)

        gmsh.model.occ.synchronize()

        return result_tags

    @optional_features
    def _create_wedge_geom(self, surface_inner: WedgeSurface, surface_outer: WedgeSurface) -> None:
        """
        Create a wedge geometry based on two input surfaces.

        Args:
            surface_inner (Surface): The inner surface of the wedge.
            surface_outer (Surface): The outer surface of the wedge.

        Returns:
            Solid: The generated wedge geometry.

        Raises:
            Exception: If the wedge could not be generated from the input surfaces.
        """
        points_front_bottom = surface_outer.lower_edge
        points_front_top = surface_outer.upper_edge
        points_back_bottom = surface_inner.lower_edge
        points_back_top = surface_inner.upper_edge
        self._make_wedge(points_front_bottom, points_front_top, points_back_bottom, points_back_top)

    def set_conductor_order(self, coils: dict[int, Coil3DGeometry]) -> None:
        """Find a ordered list of connected conductors for all coil blocks.

        Stores continuity and append to name of exported conductors.

        This function iterates through all coils, finds connected conductors (via proximity of the ends
        between conductors) and generates a list of conductor groups, each group containing a list of conductors
        in order of connection. Iterating over the resulting list will lead to a continuous coil from end to end.



        :param coils: The coils to be processed.
        :type coils: dict[int, Coil3DGeometry]

        :return: A list of lists, where each inner list contains the ordered conductor IDs for one continuous coil.

        """
        self._prepend_continuity_order = True
        conductor_points = {}
        for geom_id, geom in coils.items():
            p_s = np.mean(geom.geometry.nodes[:4], axis=0)
            p_e = np.mean(geom.geometry.nodes[-4:], axis=0)
            conductor_points[geom_id] = (p_s, p_e)

        base_cond = 2
        base_s, base_e = conductor_points[base_cond]
        nr_cond = len(conductor_points)
        threshold = 0.5

        connectivity = csr_array((nr_cond, nr_cond), dtype=int)
        for geom1, (s1, e1) in conductor_points.items():
            nr_conn = []
            for geom2, (s2, e2) in conductor_points.items():
                if geom1 == geom2:
                    continue
                dist_e1_e2 = np.linalg.norm(e2 - e1)
                dist_s1_s2 = np.linalg.norm(s2 - s1)
                if dist_e1_e2 < threshold:
                    connectivity[geom1 - 1, geom2 - 1] = 1
                    nr_conn.append(geom2)
                if dist_s1_s2 < threshold:
                    connectivity[geom1 - 1, geom2 - 1] = 1
                    nr_conn.append(geom2)
        degrees = connectivity.sum(axis=1)
        start_end_nodes = set([i for i in range(nr_cond) if degrees[i] == 1])
        all_nodes = set(range(nr_cond))
        orders = []
        while start_end_nodes:
            n = start_end_nodes.pop()
            node_list = breadth_first_order(connectivity, n, directed=False, return_predecessors=False)
            node_set = set(node_list)
            all_nodes -= node_set
            start_end_nodes -= node_set
            orders.append([c + 1 for c in node_list])
        if all_nodes:
            logger.warning(
                f"There are still conductors which could not be assigned to groups: {[c + 1 for c in all_nodes]}"
            )

        order_dict = {}
        for oidx, order in enumerate(orders):
            for cidx, c in enumerate(order):
                order_dict[c] = (oidx, cidx)  # Adjusting for 1-based indexing

        self._conductor_order_dict = order_dict
        self._conductor_orders = orders


class StepGeneratorFromCoil(StepGeneratorBase):
    """
    Stepfile Generator using only coil definitions to generate the geometry.

    This class is ignoring roxie generated wedge definitions, and generates endspacers directly from a coil definition.
    The results can be more stable and consistent over roxie generated wedges, but need more input data for generation
    """

    def __init__(self, n_straight=1) -> None:
        super().__init__(n_straight=n_straight)
        self.logger = logging.getLogger("StepGeneratorFromCoil")
        self._add_ins_r: Optional[float] = None
        self._add_ins_phi: Optional[float] = None
        self._coil_block_radii: dict[int, tuple[float, float]] = {}
        self._layer_order: dict[int, list[int]] = {}
        self._layer_blocks: dict[int, list[int]] = {}
        self._layer_quadrants: dict[int, set[int]] = {}
        self._layer_symmetry: dict[int, int] = {}
        self._block_part_numbers: dict[int, int] = {}
        self._layer_max_z: dict[int, float] = {}

    def fill_parameters(
        self,
        roxie_input: RoxieInputBuilder,
        roxie_output: RoxieOutputParser,
        coilblock_dr=0.5,
        opt_nr=1,
    ) -> None:
        """Fill the parameters for the step generator from a roxie input and output.

        :param roxie_input: The roxie input object to get the parameters from
        :param roxie_output: The roxie output object to get the parameters from
        """
        self.set_cable_parameters(roxie_output.opt[opt_nr].blockTopologies)
        layer_order: dict[float, list[int]] = {}
        for _, row in roxie_input.layer.iterrows():
            layer_nr = row.no
            layer_symmetry = row.symm // 2
            self._layer_symmetry[layer_nr] = layer_symmetry
            blocks = row.blocks
            block_radii = [roxie_input.block.loc[roxie_input.block["no"] == b, "radius"].iloc[0] for b in blocks]
            std = np.std(block_radii)
            if std > 10e-3:
                logger.warning(
                    f"Variadion in radii within blocks in layer {layer_nr}:",
                    f"{[(bl, r) for bl, r in zip(blocks, block_radii)]}. ",
                    f"Using {block_radii[0]} as radius.",
                )
            r = round(block_radii[0], 2)
            if r not in layer_order:
                layer_order[r] = []
            layer_order[r].append(layer_nr)

        layer_items = list(layer_order.items())
        layer_items.sort(key=lambda x: x[0])  # Sort by radius
        if len(layer_items) >= 2:
            layer_delta = layer_items[1][0] - layer_items[0][0]
            for r, layers in layer_items:
                for la in layers:
                    self._coil_block_radii[la] = (r - coilblock_dr, r + layer_delta + coilblock_dr)
        else:
            logger.warning(
                "There is only one layer, please set coil block manually by calling ",
                "set_coil_block_radii(layer_nr,r_inner,r_outer)",
            )
        self._layer_order = {i + 1: layer_order[r] for i, r in enumerate(layer_order.keys())}
        self._layer_blocks = {}
        for _, top in roxie_output.opt[opt_nr].blockTopologies.items():
            layer_nr = top.layer_nr
            if layer_nr not in self._layer_blocks:
                self._layer_blocks[layer_nr] = []
            self._layer_blocks[layer_nr].append(top.block_nr)

        self._set_block_parameters(roxie_output.opt[opt_nr].coilGeometries3D)

    def set_layer_symmetry(self, layer_nr: int, symmetry: int):
        """
        Set the symmetry type of a layer. This is used to determine the number of blocks in a layer.

        :param layer_nr: Layer number to apply symmetry
        :type layer_nr: int
        :param symmetry:
            The symmetry of the layer. 1 = dipole, 2 = quadrupole, 3 = sextupole, ...
        """
        self._layer_symmetry[layer_nr] = symmetry

    def set_coil_block_radii(self, layer_nr: int, inner_radius: float, outer_radius: float):
        """
        Set the inner and outer radii of the former for a given layer.

        :param layer_nr: Layer number to apply radii
        :type layer_nr: int
        :param inner_radius:
            The inner radius of the block geometry. The coil
            block can be used as a tool for the boolean operation
            to determine the endspacer, wedge and post geometry.
        :param outer_radius:
            The outer radius of the block geometry. The coil
            block can be used as a tool for the boolean operation
            to determine the endspacer, wedge and post geometry.
        """
        self._coil_block_radii[layer_nr] = (inner_radius, outer_radius)

    def set_former_insulation(self, add_ins_r: float, add_ins_phi: float):
        """Add insulation to former geometry
        :param add_ins_r:
            The thickness of the insulation in r direction.
        :type add_ins_r: float

        :param add_ins_phi:
            The thickness of the insulation in phi direction.
        :type add_ins_phi: float
        """
        self._add_ins_r = add_ins_r
        self._add_ins_phi = add_ins_phi

    def _set_block_parameters(self, coils) -> None:
        """Set max Z extend and block part numbers for all coilblocks.

        The block part number is defined as one block plus it's symmetry component.
        E.g for Dipoles, there are 2 coil block parts, for quadrupoles 4, sextupoles 6, etc.
        Coil block parts for Z<0 are negative, for Z>0 positive.


        :return: The block part number.
        :rtype: int
        """

        for _, c in coils.items():
            max_z = np.abs(c.geometry.nodes[:, 2]).max()
            self._layer_max_z[c.layer_id] = max(
                self._layer_max_z.get(c.layer_id, 0.0),
                max_z,
            )
            if c.block_id not in self._block_part_numbers:
                layer_nr = c.layer_id
                if layer_nr not in self._layer_symmetry:
                    raise ValueError(f"Layer {layer_nr} has no symmetry set. Use set_layer_symmetry to set it")
                if c.geometry.nodes is None:
                    raise ValueError(f"Coil {c.nr} has no geometry nodes set. Cannot determine block part number")
                z_inner = c.geometry.nodes[-1, 2]
                cable_phi = np.arctan2(c.geometry.nodes[0, 1], c.geometry.nodes[0, 0])
                if cable_phi < 0:
                    cable_phi += 2 * math.pi
                bpn_float = cable_phi / (math.pi / self._layer_symmetry[layer_nr])
                block_part_nr = int(bpn_float) + 1
                if z_inner < 0:
                    block_part_nr = -block_part_nr

                self._block_part_numbers[c.block_id] = block_part_nr

    def _get_corner_order(self, layer_nr: int, nodes: np.ndarray) -> tuple[int, int, int, int, int]:
        symm = self._layer_symmetry[layer_nr]
        z_inner = nodes[-1, 2]
        cable_phi = np.arctan2(nodes[0, 1], nodes[0, 0])
        imag = cable_phi / (np.pi / symm / 2) // 1 % 2 == 1

        quadrant = 2 if imag else 1
        if z_inner < 0:
            quadrant += 2

        if quadrant == 1:
            p1 = 0
            p2 = 1
            p3 = 2
            p4 = 3
        elif quadrant == 2:
            p1 = 1
            p2 = 0
            p3 = 3
            p4 = 2
        elif quadrant == 3:
            p1 = 3
            p2 = 2
            p3 = 1
            p4 = 0
        elif quadrant == 4:
            p1 = 2
            p2 = 3
            p3 = 0
            p4 = 1

        quadr = math.floor(cable_phi % (np.pi / symm / 2))

        return p1, p2, p3, p4, quadr

    def _calculate_coil_block(self, coils: dict[int, Coil3DGeometry], block_number: int, debug=False):
        coil_blocks = [idx for idx, coil in coils.items() if coil.block_id == block_number]
        inner_cable_number = min(coil_blocks)
        outer_cable_number = max(coil_blocks)

        layer_nr = coils[inner_cable_number].layer_id
        if layer_nr not in self._coil_block_radii:
            raise ValueError(
                f"Layer {layer_nr} has no inner and outer coil block radius set. Use set_coil_block_radii to set them"
            )
        inner_radius = self._coil_block_radii[layer_nr][0]
        outer_radius = self._coil_block_radii[layer_nr][1]

        # the inner cable
        inner_cable = coils[inner_cable_number]
        outer_cable = coils[outer_cable_number]

        ins_r = self._get_ins_r(block_number)
        ins_phi = self._get_ins_phi(block_number)

        if self._add_ins_r:
            ins_r += self._add_ins_r
        if self._add_ins_phi:
            ins_phi += self._add_ins_phi

        if inner_cable.geometry.elements is None or outer_cable.geometry.elements is None:
            raise ValueError("Cable geometries are lacking connectivity information")

        # add the insulation to the nodes
        p_inner = add_insulation_thickness(inner_cable.geometry.nodes, inner_cable.geometry.elements, ins_r, ins_phi)
        p_outer = add_insulation_thickness(outer_cable.geometry.nodes, outer_cable.geometry.elements, ins_r, ins_phi)

        p1, p2, p3, p4, quadr = self._get_corner_order(layer_nr, inner_cable.geometry.nodes)

        if layer_nr not in self._layer_quadrants:
            self._layer_quadrants[layer_nr] = set()
        self._layer_quadrants[layer_nr].add(quadr)

        r_0_pre = p_inner[p2::4, :]
        r_1_pre = p_outer[p1::4, :]

        # the directions of the generators
        g_30 = normalize_vectors(inner_cable.geometry.nodes[p3::4, :] - inner_cable.geometry.nodes[p2::4, :])
        g_21 = normalize_vectors(outer_cable.geometry.nodes[p4::4, :] - outer_cable.geometry.nodes[p1::4, :])

        # extend the upper edges of the coil block
        r_3, _ = get_intersection_line_cylinder(r_0_pre, g_30, outer_radius, debug=debug)

        r_2, _ = get_intersection_line_cylinder(r_1_pre, g_21, outer_radius, debug=debug)

        # extend the lower edges of the coil block
        r_0, _ = get_intersection_line_cylinder(r_0_pre, g_30, inner_radius, debug=debug)

        r_1, _ = get_intersection_line_cylinder(r_1_pre, g_21, inner_radius, debug=debug)

        return r_3, r_2, r_0, r_1

    def _make_coil_block_es(self, coils: dict[int, Coil3DGeometry], block_number: int) -> list[tuple[int, int]]:
        """Create a coil block for endspacer generation"""
        coil_block_radii_bu = copy.copy(self._coil_block_radii)

        try:
            for layer_nr, radii in self._coil_block_radii.items():
                self._coil_block_radii[layer_nr] = (
                    radii[0] - 5,
                    radii[1] + 5,
                )

            r_3, r_2, r_0, r_1 = self._calculate_coil_block(coils, block_number)
            points_front_bottom = r_2
            points_front_top = r_3
            points_back_bottom = r_1
            points_back_top = r_0
            return self._make_wedge(points_front_bottom, points_front_top, points_back_bottom, points_back_top)
        finally:
            self._coil_block_radii = coil_block_radii_bu  # restore the radii after the calculation

    def get_coil_block_geom(
        self,
        coils: dict[int, Coil3DGeometry],
        block_number: int,
    ) -> None:
        """Make a step file for a coil block.

        :param directory:
            The directory with the .xml file.

        :param filename:
            The filename.

        :param block_number:
            The block number to specify the filename.

        :return:
            None
        """
        r_3, r_2, r_0, r_1 = self._calculate_coil_block(coils, block_number)

        if not self.model_color:
            self.model_color = [0x9E, 0x18, 0x02]  # Default color red
        if self.model_name is None:
            self.set_model_name(f"coilblock_{block_number:03d}")

        self._create_wedge_geom(WedgeSurface(r_1, r_0), WedgeSurface(r_2, r_3))

    def get_all_coil_block_geoms(self, coils: dict[int, Coil3DGeometry]) -> None:
        """
        Generate the geometry of all coil blocks.

        :param coils: all coils

        :return: None
        """
        # Extract coil blocksü
        coil_blocks = {coil.block_id for coil in coils.values()}

        for cb in tqdm(coil_blocks, desc="Generating coil block geometries"):
            self.get_coil_block_geom(coils, cb)

    @apply_post_funcs
    def _store_single_spacer(self, spacer: tuple[int, int], all_spacers: list[tuple[int, int]]) -> None:
        for sp1 in all_spacers:
            visibility = 1 if sp1 == spacer else 0
            gmsh.model.setVisibility([sp1], visibility, recursive=True)

    @gmsh_cleanup
    @apply_pre_funcs
    def _create_spacers(
        self,
        coils: dict[int, Coil3DGeometry],
        radial_nr=1,
        angular_nr=1,
        add_z: float = 20.0,
        zmax: Optional[float] = None,
    ) -> None:
        layers = self._layer_order[radial_nr]
        block_ids = set()
        for layer_nr in layers:
            for bl in self._layer_blocks[layer_nr]:
                if self._block_part_numbers[bl] == angular_nr:
                    block_ids.add(bl)
        radius_inner, radius_outer = self._coil_block_radii[layers[0]]
        order = self._layer_symmetry[layers[0]]
        # Load steps
        blocks_step = []
        for block in tqdm(block_ids, desc="Generate coil block"):
            shapes = self._make_coil_block_es(coils, block)
            blocks_step.extend(shapes)

        if not zmax:
            zmax = self._layer_max_z[layer_nr] + add_z
            if angular_nr < 0:
                zmax = -zmax

        # Create base cylinder of the spacers
        with tqdm(total=3, desc="Create cylinder, cut") as pbar:
            seg_span = math.pi / order
            rect = gmsh.model.occ.addRectangle(radius_inner, 0, 0, radius_outer - radius_inner, zmax)
            # Rotate into z axis
            gmsh.model.occ.rotate([(2, rect)], 0, 0, 0, 1, 0, 0, math.pi / 2)
            # Rotate to start of angular_segment
            gmsh.model.occ.rotate([(2, rect)], 0, 0, 0, 0, 0, 1, seg_span * (abs(angular_nr) - 1))
            cyl_segment = gmsh.model.occ.revolve([(2, rect)], 0, 0, 0, 0, 0, 1, seg_span)
            pbar.update(1)
            pbar.set_postfix_str("Cylinder done")
            dimtags = gmsh.model.occ.cut([(3, cyl_segment[1][1])], blocks_step, removeTool=True)
            pbar.update(1)
            pbar.set_postfix_str("Cut done")
            spacers = list(dimtags[0])

            gmsh.model.occ.synchronize()
            ent_2d = gmsh.model.getEntities(2)
            gmsh.model.occ.remove(ent_2d)
            ent_1d = gmsh.model.getEntities(1)
            gmsh.model.occ.remove(ent_1d)
            ent_0d = gmsh.model.getEntities(0)
            gmsh.model.occ.remove(ent_0d)
            gmsh.model.occ.synchronize()
            pbar.update(1)
            pbar.set_postfix_str("cleanup done")

        # Sort spacers by their z position
        def maxabsz(dimtag):
            """Get the maximum absolute z-coordinate of the bounding box of a given entity."""
            _, _, zmin, _, _, zmax = gmsh.model.getBoundingBox(*dimtag)
            return max(abs(zmin), abs(zmax))

        spacers.sort(key=maxabsz)  # Sort by z-coordinate of bounding box
        spacer_names = [f"_{i}_spacer" for i in range(len(spacers))]
        spacer_names[0] = "_0_inner_post"
        spacer_names[-1] = f"_{len(spacer_names) - 1}_headspacer"

        gmsh.option.setNumber("Geometry.OCCExportOnlyVisible", 1)
        model_name_bu = self.model_name
        if self.model_name is None:
            model_name_bu = f"spacers_rp_{radial_nr}_ap_{angular_nr}"
        try:
            for spacer, sn in tqdm(zip(spacers, spacer_names), total=len(spacer_names), desc="Extract single spacers"):
                self.model_name = model_name_bu + sn
                self._store_single_spacer(spacer, spacers)
        finally:
            for spacer in spacers:
                gmsh.model.setVisibility([spacer], 1, recursive=True)
            gmsh.option.setNumber("Geometry.OCCExportOnlyVisible", 0)

    def get_endspacer_geom(
        self,
        coils: dict[int, Coil3DGeometry],
        radial_nr=1,
        angular_nr=1,
        add_z: float = 20.0,
        zmax: Optional[float] = None,
    ) -> None:
        """Create spacer geometries (former).

        :param coils: The coils to generate spacers from
        :param radial_nr: The radial number of the layer to generate spacers from (inner to outer)
        :param angular_nr: The angular number of the layer to generate spacers from (math. positive direction)
                           For dipole, this is 1 or 2, for quadrupole 1, 2, 3, or 4, etc.
                           For Formers in Z<0, this is negative, for Z>0 positive.
        :param add_z: Additional z extension of endspacer
        :param zmax: Optional: Maximum z extension of endspacer (ignore add_z and actual length of coils)

        :return: None
        """
        if not self.model_color:
            self.model_color = [0xFF, 0xA5, 0x00]  # Default color red
        if not self.model_name:
            self.set_model_name(f"spacers_rp_{radial_nr}_ap_{angular_nr}")
        self._create_spacers(coils, radial_nr, angular_nr, add_z, zmax)

    def get_all_endspacer_geoms(
        self,
        coils: dict[int, Coil3DGeometry],
        add_z: float = 20.0,
        zmax: Optional[float] = None,
    ) -> None:
        """Generate the geometry of all spacers.
        :param coils: The coils to generate spacers from
        :param add_z: Additional z extension of endspacer
        :param zmax: Optional: Maximum z extension of endspacer (ignore add_z and actual length of coils)
        :return: None
        """
        bpn_vals = set(self._block_part_numbers.values())
        items = list(itertools.product(self._layer_order, bpn_vals))
        for lo, bpn in tqdm(
            items,
            desc="Generating endspacer geometries",
        ):
            self.get_endspacer_geom(
                coils,
                radial_nr=lo,
                angular_nr=bpn,
                add_z=add_z,
                zmax=zmax,
            )

    def get_from_parser(  # type: ignore[override]
        self,
        parser: RoxieOutputParser,
        opt_step: int = 1,
        generate_conductors: bool = True,
        generate_coil_blocks: bool = True,
        generate_endspacers: bool = True,
        add_z: float = 20.0,
        z_max: Optional[float] = None,
    ) -> None:
        """
        From a parsed roxie output, get CAD geometries for endspacers, coil blocks, and conductors.

        :param parser: (RoxieOutputParser) The parser object to retrieve geometries from.
        :param opt_step: (int) The optimization step number. Defaults to 1
        :param generate_endspacers: (bool) Whether to generate endspacers geometries. Defaults to True.
        :param generate_coil_blocks: (bool) Whether to generate coil block geometries. Defaults to True.
        :param generate_conductors: (bool) Whether to generate conductor geometries. Defaults to True.

        :param add_z: Additional extension in z direction for headspacers (from coil maximum).
        :param z_max: Alternative: Fixed maximum z length of headspacers

        :return: None
        """
        if generate_conductors:
            self.get_all_coil_geoms(parser.opt[opt_step].coilGeometries3D)
        if generate_coil_blocks:
            self.get_all_coil_block_geoms(parser.opt[opt_step].coilGeometries3D)
        if generate_endspacers:
            self.get_all_endspacer_geoms(parser.opt[opt_step].coilGeometries3D, add_z=add_z, zmax=z_max)


StepGenerator = StepGeneratorFromCoil
