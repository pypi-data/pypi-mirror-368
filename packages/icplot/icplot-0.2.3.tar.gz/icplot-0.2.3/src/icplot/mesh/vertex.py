from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from icplot.geometry import Point, Vector, get_point_distance


@dataclass(frozen=True)
class Vertex:
    """
    A mesh vertex
    """

    x: float
    y: float
    z: float = 0.0
    id: int = -1

    @staticmethod
    def from_point(p: Point, id: int = -1) -> Vertex:
        return Vertex(p.x, p.y, p.z, id)

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def get_distance(self, p: Point) -> float:
        return get_point_distance(p.as_array(), self.as_array())

    def get_vertex_distance(self, v: Vertex) -> float:
        return get_point_distance(v.as_array(), self.as_array())

    def translate(self, v: Vector) -> Vertex:
        return Vertex(self.x + v.x, self.y + v.y, self.z + v.z, self.id)


def find_closest(verts: list[Vertex], point: Point) -> int:

    if not verts:
        raise RuntimeError("Can't find nearest vert in empty list")

    min_id = -1
    min_distance = 0.0
    for idx, v in enumerate(verts):

        distance = v.get_distance(point)

        if idx == 0:
            min_id = idx
            min_distance = distance
            continue

        if distance < min_distance:
            min_id = idx
            min_distance = distance

    return min_id
