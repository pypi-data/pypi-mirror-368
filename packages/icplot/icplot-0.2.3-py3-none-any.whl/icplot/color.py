"""
This module handles colors
"""

from typing import Callable

from pydantic import BaseModel


class Color(BaseModel, frozen=True):
    """
    A color class, internal storage is rgba as float.
    """

    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

    @staticmethod
    def from_rgba(r: float = 0.0, b: float = 0.0, g: float = 0.0, a: float = 1.0):
        return Color(**{"r": r, "g": g, "b": b, "a": a})

    @staticmethod
    def from_list(data: list):
        return Color(**{"r": data[0], "g": data[1], "b": data[2]})

    def as_list(self) -> list:
        return [self.r, self.g, self.b]

    def is_black(self) -> bool:
        return self.r == 0.0 and self.g == 0.0 and self.b == 0.0 and self.a == 1.0


class ColorMap:
    """
    A mapping from a flat index to a color
    """

    def __init__(self, label: str, data_func: Callable):
        self.label = label
        self.data_func = data_func

    def get_color(self, cursor: int, count: int) -> Color:
        """
        Returns a colour based on a cmap and how far across
        the datasets you are
        """
        position = cursor / (max(count - 1, 1))
        return Color.from_list(self.data_func(position))
