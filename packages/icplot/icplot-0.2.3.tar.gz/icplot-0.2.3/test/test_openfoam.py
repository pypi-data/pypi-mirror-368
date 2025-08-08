from iccore.test_utils import get_test_output_dir

from icplot.geometry import Transform, Point, Cylinder, Cuboid
from icplot.mesh import openfoam, vtk, mesh_cylinder, mesh_cuboid


def test_closest_edge():

    cuboid = Cuboid()

    mesh = mesh_cuboid(cuboid)

    closest_edge = mesh.get_closest_edge(Point(0.0, -0.5, -0.5))

    assert closest_edge[0] == 0
    assert closest_edge[1] == 1


def test_mesh():

    output_dir = get_test_output_dir()

    cylinder = Cylinder(Transform(Point(0.0, 0.0, 0.0)), length=2.0, diameter=1.0)

    mesh = mesh_cylinder(cylinder)
    vtk.write_unstructured_grid(mesh, output_dir / "cylinder.vtk")
    # return

    foam_str = openfoam.write_blockmesh(mesh)

    assert foam_str

    if not openfoam.has_blockmesh():
        return

    openfoam.generate_mesh(mesh, output_dir)
