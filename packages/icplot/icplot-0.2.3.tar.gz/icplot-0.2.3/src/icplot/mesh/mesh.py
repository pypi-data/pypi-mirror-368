"""
Module for describing mesh elements. Goes for simplicity and low dependencies
over performance. Consider something else for high performance meshing.
"""

from __future__ import annotations
from dataclasses import dataclass

from icplot.geometry import Point, Vector, Transform, Bounds

from .vertex import Vertex
from .cell import Cell
from .edge import Edge, contains_point, get_distance


@dataclass(frozen=True)
class Patch:
    """
    A collection of mesh faces - used for openfoam boundaries
    """

    type: str
    name: str
    faces: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class Mesh:

    vertices: tuple[Vertex, ...]
    cells: tuple[Cell, ...]
    scale: float = 1.0
    edges: tuple[Edge, ...] = ()
    patches: tuple[Patch, ...] = ()

    def get_bounds(self) -> Bounds:
        if len(self.vertices) == 0:
            raise RuntimeError("Can't get bounds on empty mesh")

        xmin = self.vertices[0].x
        xmax = xmin
        ymin = self.vertices[0].y
        ymax = ymin
        zmin = self.vertices[0].z
        zmax = zmin
        for v in self.vertices:
            xmin = min(xmin, v.x)
            xmax = max(xmax, v.x)
            ymin = min(ymin, v.y)
            ymax = max(ymax, v.y)
            zmin = min(zmin, v.z)
            zmax = min(zmax, v.z)
        return Bounds(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, zmin=zmin, zmax=zmax)

    def get_location(self) -> Vector:
        bounds = self.get_bounds()
        return Vector(bounds.xmin, bounds.ymin, bounds.zmin)

    def apply_transform(self, t: Transform) -> Mesh:
        delta = t.location.subtract(self.get_location())
        return Mesh(
            vertices=tuple(v.translate(delta) for v in self.vertices), cells=self.cells
        )

    def select_edge(self, p: Point) -> tuple[int, int]:

        for c in self.cells:
            for e in c.get_edges():
                if contains_point(self.vertices[e[0]], self.vertices[e[1]], p):
                    return (e[0], e[1])
        raise RuntimeError("No edge found at selection point")

    def get_closest_edge(self, p: Point) -> tuple[int, int]:

        min_dist = -1.0
        closest_edges: tuple[int, int] = (-1, -1)
        for b in self.cells:
            for e in b.get_edges():
                dist = get_distance(self.vertices[e[0]], self.vertices[e[1]], p)
                if min_dist == -1.0:
                    min_dist = dist
                    closest_edges = (e[0], e[1])
                    continue
                if dist < min_dist:
                    min_dist = dist
                    closest_edges = (e[0], e[1])
        return closest_edges
