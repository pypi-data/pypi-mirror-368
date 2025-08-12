# SPDX-FileCopyrightText: 2024 CERN
#
# SPDX-License-Identifier: BSD-4-Clause

"""Interfacing Roxie with external geometry generation"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


# As Python class stub (roxieinterfaces packages, not yet implemented)
@dataclass
class Point2D:
    x: float
    y: float


@dataclass
class Point3D(Point2D):
    z: float
    s: float


@dataclass
class Conductor:
    block: int
    current: float
    crossection: Tuple[Point2D, Point2D, Point2D, Point2D]
    crossection_ins: Tuple[Point2D, Point2D, Point2D, Point2D]
    conductor_3d: List[Tuple[Point3D, Point3D, Point3D, Point3D]]
    DARBTORSION: List[float]
    DARBNORMA: List[float]
    DARBGEODE: List[float]


class ExtGeo2Roxie:
    """Data structure holding all information to be send to Roxie"""

    def __init__(self) -> None:
        self.conductors: List[Conductor] = []

    def add_conductor(self, cond: Conductor) -> None:
        pass

    def to_file(self, filename: Path = Path("ext2roxie.txt")) -> None:
        """Write data structures to file"""
        pass
