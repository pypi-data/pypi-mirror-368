"""
Module for primitive geometries. This is used to keep dependencies simple,
consider a real geometry library like cgal for more complex or performance
dependent work.
"""

from __future__ import annotations
from dataclasses import dataclass

from .base import Point, Vector
from .transform import Transform


@dataclass(frozen=True)
class Shape:
    """
    A shape in 3d space, defaults to having a normal to Z
    """

    transform: Transform = Transform()


@dataclass(frozen=True)
class Circle(Shape):

    radius: float = 1.0


@dataclass(frozen=True)
class Annulus(Shape):

    outer_radius: float = 1.0
    inner_radius: float = 0.5
    angle: float = 360  # degrees


@dataclass(frozen=True)
class Quad(Shape):
    """
    A regular quadrilateral in 3d space, defaults to be normal to Z
    """

    width: float = 1.0
    height: float = 1.0

    @property
    def points(self) -> list[Point]:

        locs = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

        points = [
            self.transform.get_point_at_offset(
                self.width * loc[0], self.height * loc[1], 0.0
            )
            for loc in locs
        ]
        points = self.transform.centre_points(points)
        return self.transform.align_points_with_normal(points)

    def translate(self, v: Vector) -> Quad:
        return Quad(self.transform.translate(v), self.width, self.height)


@dataclass(frozen=True)
class Cuboid(Shape):
    """
    A regular cuboid
    """

    width: float = 1.0
    height: float = 1.0
    depth: float = 1.0
    top_width_scale: float = 1.0

    def translate(self, v: Vector) -> Cuboid:
        return Cuboid(self.transform.translate(v), self.width, self.height, self.depth)

    @property
    def points(self) -> list[Point]:

        base = Quad(
            self.transform.translate(Vector(0.0, 0.0, -self.depth / 2.0)),
            self.width,
            self.height,
        )

        top = Quad(
            self.transform.translate(Vector(0.0, 0.0, -self.depth / 2.0)),
            self.width * self.top_width_scale,
            self.height,
        )
        top = top.translate(self.transform.normal.scale(self.depth))
        return base.points + top.points


@dataclass(frozen=True)
class Cylinder(Shape):
    """
    A cylinder
    """

    diameter: float = 1.0
    length: float = 1.0

    @property
    def start(self) -> Point:
        return self.transform.location

    @property
    def end(self) -> Point:
        return self.transform.get_point_at_normal_offset(self.length)


@dataclass(frozen=True)
class Revolution(Shape):
    """
    A revolved profile sitting on the plane given by the loc
    and normal and revolved about the normal.
    """

    diameter: float = 1.0
    length: float = 1.0
    profile: str = "arc"


@dataclass(frozen=True)
class CuboidGrid:
    """
    A irregular grid composed of cuboids. Can be useful for
    generating topological meshes like OpenFoam's blockMesh.
    """

    x_locs: list[float]
    y_locs: list[float]
    z_locs: list[float]

    @property
    def cuboids(self) -> list[Cuboid]:
        ret = []

        for kdx, z in enumerate(self.z_locs[:-1]):
            for jdx, y in enumerate(self.y_locs[:-1]):
                for idx, x in enumerate(self.x_locs[:-1]):
                    width = self.x_locs[idx + 1] - x
                    height = self.y_locs[jdx + 1] - y
                    depth = self.z_locs[kdx + 1] - z
                    ret.append(
                        Cuboid(
                            Transform(location=Point(x, y, z)),
                            width=width,
                            height=height,
                            depth=depth,
                        )
                    )
        return ret
