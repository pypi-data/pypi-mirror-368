from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from .base import Point, Vector
from .operations import get_three_point_normal, get_rotation_matrix


_GLOBAL_Z = np.array([0.0, 0.0, 1.0])


def get_normal_from_points(p0: Point, p1: Point, p2: Point):
    return get_three_point_normal(p0.as_array(), p1.as_array(), p2.as_array())


@dataclass(frozen=True)
class Transform:
    location: Point = Point(0.0, 0.0, 0.0)
    normal: Vector = Vector(0.0, 0.0, 1.0)
    scale: Vector = Vector(1.0, 1.0, 1.0)
    angle: float = 0.0  # degrees

    def translate(self, v: Vector) -> Transform:
        return Transform(
            self.location.translate(v), self.normal, self.scale, self.angle
        )

    def get_point_at_offset(self, x: float, y: float, z: float = 0.0) -> Point:
        return self.location.translate(Vector(x, y, z))

    def get_point_at_normal_offset(self, offset: float) -> Point:
        return self.location.translate(self.normal.scale(offset))

    def get_rotation_matrix(self, relative_to: Vector | None = None):
        if relative_to:
            return get_rotation_matrix(relative_to.as_array(), self.normal.as_array())
        return get_rotation_matrix(_GLOBAL_Z, self.normal.as_array())

    def centre_points(self, points: list[Point]) -> list[Point]:
        x = sum(p.x for p in points) / len(points)
        y = sum(p.y for p in points) / len(points)
        z = sum(p.z for p in points) / len(points)
        delta = self.location.subtract(Vector(x, y, z))
        return [p.translate(delta) for p in points]

    def align_points_with_normal(self, points: list[Point]) -> list[Point]:

        rot = self.get_rotation_matrix()
        rotated_points = [
            Point.from_array(
                rot.dot(p.as_array() - self.location.as_array())
                + self.location.as_array()
            )
            for p in points
        ]

        plane_normal = get_normal_from_points(
            rotated_points[0],
            rotated_points[1],
            rotated_points[3],
        )

        if np.dot(plane_normal, self.normal.as_array()) < 0:
            rotated_points.reverse()
        return rotated_points
