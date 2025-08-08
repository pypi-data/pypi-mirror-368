from dataclasses import dataclass

from icplot.geometry import Point, segment_contains_point, get_segment_distance

from .vertex import Vertex


@dataclass(frozen=True)
class Edge:
    """
    A mesh edge - consists of two verts
    """

    vert0: int
    vert1: int
    type: str = "line"
    interp_points: tuple[Point, ...] = ()


def contains_point(v0: Vertex, v1: Vertex, p: Point, tol: float = 1.0e-4) -> bool:
    """
    True if the edge given by v0 and v1 contains point p
    """
    return segment_contains_point(v0.as_array(), v1.as_array(), p.as_array(), tol)


def get_distance(v0: Vertex, v1: Vertex, p: Point) -> float:
    """
    Return the distance between the point and the edge
    """
    return get_segment_distance(v0.as_array(), v1.as_array(), p.as_array())
