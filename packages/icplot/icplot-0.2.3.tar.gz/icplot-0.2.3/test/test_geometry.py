import pytest

from icplot.geometry import Transform, Point, Vector, Quad, Cuboid


def test_quad():

    quad = Quad(Transform(Point(0.0, 0.0, 0.0)))
    points = quad.points

    assert points[0].x == -0.5
    assert points[0].y == -0.5

    assert points[1].x == 0.5
    assert points[1].y == -0.5


def test_quad_with_rotation():

    quad = Quad(Transform(Point(0.0, 0.0, 0.0), normal=Vector(0.0, 1.0, 0.0)))
    points = quad.points

    assert points[0].x == pytest.approx(-0.5)
    assert points[0].y == pytest.approx(0.0)
    assert points[0].z == pytest.approx(0.5)

    assert points[1].x == pytest.approx(0.5)
    assert points[1].y == pytest.approx(0.0)
    assert points[1].z == pytest.approx(0.5)


def test_cuboid():

    shape = Cuboid(Transform(Point(0.0, 0.0, 0.0)))
    points = shape.points

    assert points[0].x == -0.5
    assert points[0].y == -0.5
    assert points[0].z == -0.5

    assert points[1].x == 0.5
    assert points[1].y == -0.5

    assert points[4].x == -0.5
    assert points[4].y == -0.5
    assert points[4].z == 0.5


def test_cuboid_rotation():

    return

    shape = Cuboid(Transform(Point(0.0, 0.0, 0.0), normal=Vector(0.0, 1.0, 0.0)))
    points = shape.points

    assert points[0].x == -0.5
    assert points[0].y == -0.5
    assert points[0].z == -0.5

    assert points[1].x == 0.5
    assert points[1].y == -0.5

    assert points[4].x == -0.5
    assert points[4].y == -0.5
    assert points[4].z == 0.5
