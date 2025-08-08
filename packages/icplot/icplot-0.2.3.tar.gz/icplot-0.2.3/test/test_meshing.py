from iccore.test_utils import get_test_output_dir

from icplot.geometry import Quad, Annulus, Circle
from icplot.mesh import vtk, mesh_rectangle, mesh_annulus, mesh_circle, mesh_extrude


def test_mesh_rectangle():

    output_dir = get_test_output_dir()

    rect = Quad(width=5.0, height=5.0)
    mesh = mesh_rectangle(rect, 5, 5)

    vtk.write_unstructured_grid(mesh, output_dir / "rectangle.vtk")


def test_annulus():

    output_dir = get_test_output_dir()

    shape = Annulus(outer_radius=1.0, inner_radius=0.5, angle=360)
    mesh = mesh_annulus(shape, 2, 8)

    vtk.write_unstructured_grid(mesh, output_dir / "annulus.vtk")
    vtk.write_unstructured_grid(
        mesh_extrude(mesh, 5, 5), output_dir / "annulus_extruded.vtk"
    )


def test_circle():

    output_dir = get_test_output_dir()

    shape = Circle(radius=1.0)
    mesh = mesh_circle(shape, 0.5, 2, 8)

    vtk.write_unstructured_grid(mesh, output_dir / "circle.vtk")


def test_extrude():

    output_dir = get_test_output_dir()

    rect = Quad(width=5.0, height=5.0)
    mesh = mesh_rectangle(rect, 5, 5)

    extruded_mesh = mesh_extrude(mesh, 5, 5)

    vtk.write_unstructured_grid(extruded_mesh, output_dir / "extrude.vtk")
