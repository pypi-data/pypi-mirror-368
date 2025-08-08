"""
Elements of a renderable scene
"""

from __future__ import annotations

from pydantic import BaseModel

from .color import Color


class Font(BaseModel, frozen=True):
    """
    A font spec
    """

    family: str = "Sans"
    weight: str = "normal"
    slant: str = "normal"
    size: float = 0.5


class SceneItem(BaseModel):
    """
    A base renderable model
    """

    item_type: str
    location: tuple[float, float] = (0.0, 0.0)


class Shape(SceneItem):
    """
    A base shape type
    """

    item_type: str = "shape"
    fill: Color = Color()
    stroke: Color = Color()
    stroke_thickness: float = 0.5


class TextPath(SceneItem):
    """
    Renderable text
    """

    item_type: str = "text"
    content: str
    font: Font = Font()


class Rectangle(Shape):
    """
    Renderable rectangle
    """

    item_type: str = "rect"
    w: float
    h: float


class Scene(BaseModel):
    """
    A scene with renderable items
    """

    items: list[SceneItem] = []
    size: tuple[int, int] = (100, 100)
