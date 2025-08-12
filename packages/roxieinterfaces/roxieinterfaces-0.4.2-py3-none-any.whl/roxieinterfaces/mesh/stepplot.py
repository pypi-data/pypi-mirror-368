# SPDX-FileCopyrightText: 2024 CERN
#
# SPDX-License-Identifier: BSD-4-Clause

import logging
from typing import Dict, Optional

import gmsh
import numpy as np
import pyvista as pv

from roxieinterfaces.mesh.mesh_tools import read_mesh_2D

logger = logging.getLogger(__name__)


class StepPlotter:
    def __init__(
        self,
        mesh_size_factor: float = 4,
        max_mesh_size: float = 5.0,
        store_grids: bool = True,
        plot: bool = True,
    ):
        pv.global_theme.silhouette.feature_angle = 20.0

        self._plot = plot
        self.reset()

        self.mesh_size_factor = mesh_size_factor
        self.max_mesh_size = max_mesh_size
        self.store_grids = store_grids
        self.grid_dict: Dict[str, pv.UnstructuredGrid] = {}
        self.colors = {
            "coil": [220, 80, 51],
            "coilblock": [220, 51, 64],
            "wedge": [100, 100, 230],
            "headspacer": [100, 100, 230],
            "central_post": [100, 100, 230],
        }

    def clear_grids(self):
        self.grid_dict.clear()

    @property
    def stored_grids(self) -> Dict[str, pv.UnstructuredGrid]:
        return self.grid_dict

    def reset(self):
        self.plotter = pv.Plotter() if self._plot else None

    def plot_current_gmsh_model(self, model_color: Optional[list[int]] = None):
        StepPlotter.mesh_current_model(mesh_size_factor=self.mesh_size_factor, max_mesh_size=self.max_mesh_size)
        mesh_vtk = StepPlotter.model_to_unstructured_grid()
        model_name = gmsh.model.getCurrent()
        if self.store_grids:
            self.grid_dict[model_name] = mesh_vtk
        if not model_color:
            model_color = [200, 200, 200]
        for col_name in self.colors:
            if model_name.startswith(col_name):
                model_color = self.colors[col_name]
        if self.plotter:
            StepPlotter.plot_unstructered_grid(mesh_vtk, self.plotter, model_color)

    @staticmethod
    def mesh_current_model(mesh_size_factor: float = 4.0, max_mesh_size=5.0):
        gmsh.option.setNumber("Mesh.MeshSizeFactor", mesh_size_factor)
        gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.setNumber("Mesh.MeshSizeMax", 5.0)
        gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.model.mesh.generate(2)

    @staticmethod
    def model_to_unstructured_grid() -> pv.UnstructuredGrid:
        p, c = read_mesh_2D(gmsh.model.mesh)

        cell_info = np.append(np.ones((len(c), 1), dtype=np.int32) * 3, c, axis=1)
        mesh_vtk = pv.UnstructuredGrid(cell_info, [pv.CellType.TRIANGLE] * c.shape[0], p)

        return mesh_vtk

    @staticmethod
    def plot_unstructered_grid(mesh_vtk: pv.UnstructuredGrid, plotter, color):
        surf_vtk = mesh_vtk.extract_surface()
        if surf_vtk:
            surf_vtk.compute_normals(inplace=True, split_vertices=True)

            plotter.add_mesh(
                surf_vtk,
                color=color,
                show_edges=False,
                pbr=True,
                metallic=0.2,
                roughness=0.5,
            )
            edges_vtk = surf_vtk.extract_feature_edges(45.0)
            plotter.add_mesh(edges_vtk, color="black", line_width=2)
        else:
            logger.warning("Could not extract surface from mesh")

    @staticmethod
    def mesh_and_plot_current_model(plotter, mesh_size_factor=4, color=(100, 100, 230)):
        StepPlotter.mesh_current_model(mesh_size_factor=mesh_size_factor)
        mesh_vtk = StepPlotter.model_to_unstructured_grid()
        StepPlotter.plot_unstructered_grid(mesh_vtk, plotter, color)

    @staticmethod
    def plot_step_file(filename, plotter, mesh_size_factor=4, color=(100, 100, 230)) -> None:
        """Plot a step file in pyvista. We open it in
        gmsh, mesh it and plot it.

        :param filename:
            The filename to plot.

        :param plotter:
            The pyvista plotter object to plot into.

        :param mesh_size_factor:
            The mesh size factor. This defines the mesh resolution.
            Default 10. Small values will lead to a large computation time!

        :param color:
            The color of the object.

        :return:
            None
        """

        # initialize gmsh if not done already
        if not gmsh.isInitialized():
            gmsh.initialize()

        _ = gmsh.model.occ.importShapes(filename)

        gmsh.model.occ.synchronize()
        StepPlotter.mesh_and_plot_current_model(plotter, mesh_size_factor, color)
        gmsh.clear()

        return None
