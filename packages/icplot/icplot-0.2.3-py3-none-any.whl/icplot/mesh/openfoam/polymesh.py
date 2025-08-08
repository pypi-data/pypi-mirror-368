from dataclasses import dataclass
from pathlib import Path

from icplot.mesh import Vertex

from .foamfile import read_foamfile


@dataclass(frozen=True)
class Face:
    """
    A mesh face, which is a sequence of points
    """

    points: tuple[int, ...]
    id: int = -1


@dataclass(frozen=True)
class Cell:
    """
    A mesh cell, which is a squence of faces
    """

    faces: tuple[int, ...]
    id: int = -1


@dataclass(frozen=True)
class Polymesh:
    """
    The polymesh
    """

    points: tuple[Vertex, ...]
    faces: tuple[Face, ...]
    cells: tuple[Cell, ...]


def read_polymesh(path: Path) -> Polymesh:

    points_file = read_foamfile(path / "points")
    # faces_file = read_foamfile(path / "faces")
    print(points_file)
    # print(faces_file)
    return Polymesh((), (), ())
