# SPDX-FileCopyrightText: 2024 CERN
#
# SPDX-License-Identifier: BSD-4-Clause

"""Module handling meshing"""

import argparse
import io
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import gmsh

logger = logging.getLogger(__name__)


class ElementsEnum(Enum):
    line2 = 60  # L2 Line element with two nodes
    line3 = 63  # L3 Line element with three nodes
    tria3 = 103  # T3 Triangular element with three nodes
    tria6 = 106  # T6 Triangular element with six nodes
    quad4 = 104  # Q4 Quadrilateral element with four nodes
    quad8 = 108  # Q8 Quadrilateral element with eight nodes
    tetra4 = 204  # TH4 Tetrahedral element with four nodes
    tetra10 = 210  # TH10 Tetrahedral element with ten nodes
    penta6 = 206  # P6 Pentahedral element with six nodes
    penta15 = 215  # P15 Pentahedral element with fifteen nodes
    hexa8 = 208  # H8 Hexahedral element with eight nodes
    hexa20 = 220  # H20 Hexahedral element with twenty nodes


class HmoGenerator:
    """Generate HMO files from different input sources"""

    @dataclass
    class Node:
        id: int
        x: float
        y: float
        z: float

    @dataclass
    class Element:
        id: int
        el_type: ElementsEnum
        component_id: int
        links: Tuple[int, ...]

    def __init__(self) -> None:
        self.nodes: List[HmoGenerator.Node] = []  # Nodes
        self.elements: List[HmoGenerator.Element] = []  # Element list
        self.map_components: Dict[int, str] = {}  # Material name for each component_id

    def add_component(self, id: int, material_name: str) -> None:
        """Add a new component to the list

        :param id: Component ID (linked in elements)
        :param material_name: The name of the Material (e.g BHiron1)
        """
        self.map_components[id] = material_name

    def add_node(self, id: int, x: float, y: float, z: float = 0.0) -> None:
        """Add a node to the list

        :param id: Running number of the node (needed for element connection)
        :param x: X position
        :param y: Y position
        :param z: Z position, defaults to 0.0
        """
        self.nodes.append(HmoGenerator.Node(id, x, y, z))

    def add_element(
        self,
        id: int,
        element_type: ElementsEnum,
        component_id: int,
        links: Tuple[int, ...],
    ) -> None:
        """Add a new Element to the list

        :param id: running number of element
        :param element_type: The type (e.g hexa20), see ElementsEnum for possible elements
        :param component_id: the component id of the element. With self.map_components, this defines the material
        :param links: A list of links (to nodes) as int. The order of nodes is provided in the iron file
                      definition of roxie, or here.

        Note the order of nodes
        -----------------------
        hexa20::

                            19------18-------17
                            /|              /|
                           / |             / |
                          /  12           /  11
                         /   |           /   |
                        /    |          /    |
                       /     7. . .6 . /. . .5
                     20     .         16     /
                     /     .         /      /
                    /     .         /      /
                   /     .         /      /
                  /     8         /     4
                13-------14------15     /
                 |    .          |     /
                 |   .           |    /
                 9  .           10   /
                 | .             |  /
                 |.              | /
                 |               |/
                 1-------2-------3

        """
        self.elements.append(HmoGenerator.Element(id, element_type, component_id, links))

    def load_hmascii(self, filename: Path) -> None:
        """Load a hmascii file (from Hypermesh) and bring it in internal structure

        :param filename: path to .hmascii file
        """
        ELEM_ORDER = {20: (0, 8, 1, 9, 2, 10, 3, 11, 12, 13, 14, 15, 4, 16, 5, 17, 6, 18, 7, 19)}

        with open(filename) as input_file:
            pattern = re.compile(r"\*([^(]+)\(([^\)]+)\)")
            for line in input_file:
                if line.startswith("BEGIN NODES"):
                    break
            unparsed = set()
            for line in input_file:
                if line.startswith("END NODES"):
                    break
                m = re.search(pattern, line)
                if m:
                    key = m.group(1)
                    vals = m.group(2).split(",")
                    if key == "node":
                        id = int(vals[0])
                        xyz = tuple(float(v) for v in vals[1:4])
                        self.nodes.append(HmoGenerator.Node(id, xyz[0], xyz[1], xyz[2]))
                    else:
                        unparsed.add(key)
            logger.debug(f"Total nodes: {len(self.nodes)}")
            if unparsed:
                logger.info(f"Nodes: kome keys were unparsed: {unparsed}")
            unparsed.clear()

            map_material: Dict[int, str] = {}
            unparsed = set()
            for line in input_file:
                if line.startswith("BEGIN MATERIALS"):
                    break
            for line in input_file:
                if line.startswith("END MATERIALS"):
                    break
                m = re.search(pattern, line)
                if m:
                    key = m.group(1)
                    vals = m.group(2).split(",")
                    if key == "material":
                        map_material[int(vals[0])] = vals[1]
            logger.debug(f"Total materials: {len(self.nodes)}")
            if unparsed:
                logger.info(f"Materials: some keys were unparsed:  {unparsed}")

            unparsed = set()
            current_component = -1
            for line in input_file:
                if line.startswith("BEGIN COMPONENTS"):
                    break
            for line in input_file:
                if line.startswith("END COMPONENTS"):
                    break
                m = re.search(pattern, line)
                if m:
                    key = m.group(1)
                    vals = m.group(2).split(",")
                    elem_types = ["penta6", "hexa8", "penta15", "hexa20"]
                    if key == "component":
                        current_component = int(vals[0])
                        self.map_components[int(vals[0])] = vals[1].replace('"', "")
                    elif key not in elem_types:
                        unparsed.add(key)
                    else:
                        id = int(vals[0])
                        # solver_type = int(vals[1])
                        nr_elem = len(vals[2:-1])
                        ls = []
                        for i in range(nr_elem):
                            real_idx = ELEM_ORDER[nr_elem][i]
                            ls.append(int(vals[2 + real_idx]))
                        links = tuple(ls)
                        self.elements.append(HmoGenerator.Element(id, ElementsEnum[key], current_component, links))
            logger.debug(f"Total elements: {len(self.elements)}")
            if unparsed:
                logger.info(f"Elements: Some keys were unparsed: {unparsed}")

    def renumber_items(self) -> None:
        """Renumber all entities (components, elements, nodes)
        so that they are a continuous sequence starting with 1"""
        # Components
        compontent_mapping = {}
        element_mapping = {}
        node_mapping = {}

        map_components = {}
        idx = 1
        for id, name in self.map_components.items():
            map_components[idx] = name
            compontent_mapping[id] = idx
            idx += 1
        self.map_components = map_components

        # Nodes
        idx = 1
        for node in self.nodes:
            node_mapping[node.id] = idx
            node.id = idx
            idx += 1

        # Elements
        idx = 1
        for element in self.elements:
            element_mapping[element.id] = idx
            element.id = idx
            element.component_id = compontent_mapping[element.component_id]
            element.links = tuple([node_mapping[node_id] for node_id in element.links])
            idx += 1

    def load_current_gmsh(self, default_material="BHiron1") -> None:
        """Load a GMSH file (from gmsh) and bring it in internal structure

        :param default_material: The Default material to assign to components

        """

        # Load elements from gmsh
        mapping_triangle6 = {0: 0, 1: 3, 2: 1, 3: 4, 4: 2, 5: 5}
        mapping_quad8 = {0: 0, 1: 4, 2: 1, 3: 5, 4: 2, 5: 6, 6: 3, 7: 7}
        mapping_hexa20 = {
            0: 0,
            1: 8,
            2: 1,
            3: 12,
            4: 5,
            5: 16,
            6: 4,
            7: 10,
            8: 9,
            9: 11,
            10: 18,
            11: 17,
            12: 3,
            13: 13,
            14: 2,
            15: 14,
            16: 6,
            17: 19,
            18: 7,
            19: 15,
        }
        mapping_penta15 = {
            0: 0,
            1: 7,
            2: 2,
            3: 9,
            4: 1,
            5: 6,
            6: 8,
            7: 11,
            8: 10,
            9: 3,
            10: 13,
            11: 5,
            12: 14,
            13: 4,
            14: 12,
        }
        mapping_tetra10 = {
            0: 0,
            1: 4,
            2: 1,
            3: 9,
            4: 3,
            5: 7,
            6: 6,
            7: 5,
            8: 8,
            9: 2,
        }

        nodes = gmsh.model.mesh.getNodes(includeBoundary=False)
        elements = gmsh.model.mesh.getElements()
        node_ids = nodes[0]
        node_points = nodes[1]
        node_dict = {
            node_ids[i]: (
                node_points[3 * i + 0],
                node_points[3 * i + 1],
                node_points[3 * i + 2],
            )
            for i in range(len(node_ids))
        }
        nodes_insert = {}
        idx = 0
        max_dim = 0
        for eltype in elements[0]:
            elname, eldim, elorder, _, _, _ = gmsh.model.mesh.getElementProperties(eltype)
            max_dim = max(eldim, max_dim)

        grps = gmsh.model.getPhysicalGroups(dim=max_dim)
        elem_comp_dict = {}
        max_comp_id = 0
        for grp in grps:
            name = gmsh.model.getPhysicalName(grp[0], grp[1])
            self.add_component(grp[1], name)
            elem_comp_dict.update({elem: grp[1] for elem in gmsh.model.getEntitiesForPhysicalGroup(grp[0], grp[1])})
            max_comp_id = max(max_comp_id, grp[1])
        max_comp_id += 1
        self.add_component(max_comp_id, default_material)

        for eltype, els, elnodes in zip(elements[0], elements[1], elements[2]):
            elname, eldim, elorder, _, _, _ = gmsh.model.mesh.getElementProperties(eltype)
            if eldim < max_dim:  # Skip lines and points
                continue
            if elorder != 2:
                raise Exception("Only second order meshes supported")
            for el in els:
                mapping = None
                el_nodes = None
                eltype_hmo = None
                if eltype == 9:  # 2nd order triangle
                    eltype_hmo = ElementsEnum.tria6
                    el_nodes = elnodes[idx : idx + 6]
                    # gmsh to hmo mapping so that mapping[idx_hmo]=idx_gmsh
                    mapping = mapping_triangle6
                    idx += 6
                elif eltype == 10:  # 2nd order quadrilangle
                    eltype_hmo = ElementsEnum.quad8
                    el_nodes = elnodes[idx : idx + 9]
                    mapping = mapping_quad8
                    idx += 9
                elif eltype == 16:  # 2nd order quadrilangle
                    eltype_hmo = ElementsEnum.quad8
                    el_nodes = elnodes[idx : idx + 8]
                    mapping = mapping_quad8
                    idx += 8
                elif eltype == 11:  # 2nd order Tetrahedron
                    eltype_hmo = ElementsEnum.tetra10
                    el_nodes = elnodes[idx : idx + 10]
                    mapping = mapping_tetra10
                    idx += 10
                elif eltype == 12:  # 2nd order hexahedral
                    eltype_hmo = ElementsEnum.hexa20
                    el_nodes = elnodes[idx : idx + 27]
                    mapping = mapping_hexa20
                    idx += 27
                elif eltype == 17:  # 2nd order hexahedral
                    eltype_hmo = ElementsEnum.hexa20
                    el_nodes = elnodes[idx : idx + 20]
                    mapping = mapping_hexa20
                    idx += 20
                elif eltype == 13:  # 2nd order Prism
                    eltype_hmo = ElementsEnum.penta15
                    el_nodes = elnodes[idx : idx + 18]
                    mapping = mapping_penta15
                    idx += 18
                elif eltype == 18:  # 2nd order Prism
                    eltype_hmo = ElementsEnum.penta15
                    el_nodes = elnodes[idx : idx + 15]
                    mapping = mapping_penta15
                    idx += 15
                else:
                    print(f"eltype {eltype} skipped")
                if mapping is not None and el_nodes is not None and eltype_hmo is not None:
                    for _, idx_gmsh in mapping.items():
                        node_i = el_nodes[idx_gmsh]
                        x, y, z = node_dict[node_i]
                        nodes_insert[node_i] = (x, y, z)

                    links = tuple(el_nodes[idx_gmsh] for idx_gmsh in mapping.values())
                    self.add_element(el, eltype_hmo, elem_comp_dict.get(el, max_comp_id), links)
            for idx, vals in nodes_insert.items():
                self.add_node(idx, vals[0], vals[1], vals[2])
        gmsh.finalize()
        self.renumber_items()

    def load_gmsh_file(self, filename: Path, default_material="BHiron1") -> None:
        """Load a GMSH file (from gmsh) and bring it in internal structure

        :param filename: path to .msh file
        :param default_material: The Default material to assign to components
        """

        gmsh.initialize()
        gmsh.open(str(filename))
        self.load_current_gmsh(default_material)

    def to_hmo(self) -> str:
        """Generate hmo from stored data and return as string

        :return: A string representing the hmo file
        """
        VERSION = "1.2"

        self.nodes.sort(key=lambda x: x.id)
        self.elements.sort(key=lambda x: x.id)
        # Add SuperCoils as last component
        self.map_components[len(self.map_components) + 1] = "SuperCoils"

        hmo_out = io.StringIO()

        hmo_out.write("# HYPERMESH OUTPUT FOR EDYSON CREATED WITH hmascii2hmo" + f"; VERSION={VERSION}\n")

        logger.debug(f"Writing {len(self.map_components)} material components")

        hmo_out.write("BEG_COMP_DATA\n")
        hmo_out.write(f"{len(self.map_components):7d}\n")
        for id, name in self.map_components.items():
            hmo_out.write(f"{id:8d} {name}\n")
        hmo_out.write("END_COMP_DATA\n")

        logger.debug(f"Writing {len(self.nodes)} nodes")

        hmo_out.write("BEG_NODL_DATA\n")
        hmo_out.write(f"{len(self.nodes):8d}\n")
        for node in self.nodes:
            hmo_out.write(f"{node.id:8d} {node.x:18.12e} {node.y:18.12e} {node.z:18.12e}\n")
        hmo_out.write("END_NODL_DATA\n")

        logger.debug(f"Writing {len(self.elements)} elements")

        hmo_out.write("BEG_ELEM_DATA\n")
        hmo_out.write(f"{len(self.elements):8d} ")
        # Count elems
        elem_counts: Dict[ElementsEnum, int] = defaultdict(int)
        for elem in self.elements:
            elem_counts[elem.el_type] += 1
        hmo_out.write(" ".join([f"{elem_counts[e]:8d}" for e in ElementsEnum]) + "\n")
        for elem in self.elements:
            hmo_out.write(f"{elem.id:8d} {elem.component_id:4d} {elem.el_type.value:3d} ")
            hmo_out.write(" ".join([f"{link:8d}" for link in elem.links]) + "\n")

        hmo_out.write("END_ELEM_DATA\n")
        hmo_out.write("BEG_BDRY_DATA\n")

        return hmo_out.getvalue()


def convert_hmo() -> None:
    """Script to convert an input file to hmo"""
    parser = argparse.ArgumentParser(
        description="convert different mesh formats to hmo\nSupported formats: .hmascii (Hypermesh), .msh(Gmsh)",
    )
    parser.add_argument("input_file", help="Input file to convert")
    parser.add_argument("-o", "--output", help="Output file name")
    parser.add_argument("-v", "--verbose", help="Enable debug output", action="store_true")
    parser.add_argument(
        "-m",
        "--map_material",
        help="Overwrite material mapping",
        action="append",
        nargs=2,
        metavar=("component_name", "material_name"),
    )
    args = parser.parse_args()
    output = args.output
    file = args.input_file

    material_map = args.map_material

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    filepath = Path(file)
    suf = filepath.suffix

    filepath_out = Path(filepath.with_suffix(".hmo").name) if not output else Path(output)

    logger.debug("Input file: %s", filepath)
    logger.debug("Output file: %s", filepath_out)

    hmogen = HmoGenerator()
    if suf == ".hmascii":
        hmogen.load_hmascii(filepath)
    if suf == ".msh":
        hmogen.load_gmsh_file(filepath)
    else:
        raise ValueError(f"Unknown file ending to handle, {suf}.")

    if material_map:
        replaced = False
        for component, material in material_map:
            for c, value in hmogen.map_components.items():
                if value == component:
                    hmogen.map_components[c] = material
                    replaced = True
                    logger.debug("Component id %s is now set to %s", c, material)
            if not replaced:
                logger.warning(
                    f"Component mapping: {component} not found in material list. \n    "
                    + f"Materials are: {hmogen.map_components}"
                )
    hmo = hmogen.to_hmo()
    with open(filepath_out, "w", encoding="latin-1") as output_file:
        output_file.write(hmo)
