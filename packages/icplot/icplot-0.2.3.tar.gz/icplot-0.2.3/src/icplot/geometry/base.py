from __future__ import annotations
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Vector:
    """
    A 3d spatial vector
    """

    x: float
    y: float = 0.0
    z: float = 0.0

    def scale(self, factor: float) -> Vector:
        return Vector(self.x * factor, self.y * factor, self.z * factor)

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def subtract(self, v: Vector) -> Vector:
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)


@dataclass(frozen=True)
class Point:
    """
    A location in 3d space
    """

    x: float
    y: float = 0.0
    z: float = 0.0

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    def translate(self, v: Vector) -> Point:
        return Point(self.x + v.x, self.y + v.y, self.z + v.z)

    @staticmethod
    def from_array(arr: np.ndarray) -> Point:
        return Point(arr[0], arr[1], arr[2])

    def subtract(self, v: Vector) -> Vector:
        return Vector(self.x - v.x, self.y - v.y, self.z - v.z)


@dataclass(frozen=True)
class Bounds:
    """
    A bounding box
    """

    xmin: float
    xmax: float
    ymin: float
    ymax: float
    zmin: float = 0.0
    zmax: float = 0.0
