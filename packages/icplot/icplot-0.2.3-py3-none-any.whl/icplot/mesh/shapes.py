import numpy as np

from icplot.geometry import (
    Point,
    Quad,
    Annulus,
    Transform,
    Circle,
    Cuboid,
    Vector,
    Cylinder,
)

from .mesh import Mesh
from .vertex import Vertex, find_closest
from .cell import Cell, HexCell

from .operations import map_radial, close_mesh, merge_meshes


def mesh_rectangle(rect: Quad, num_width: int = 10, num_height: int = 10) -> Mesh:

    # Generate verts
    verts: list[Vertex] = []

    delta_w = rect.width / float(num_width)
    delta_h = rect.height / float(num_height)
    count = 0
    for idx in range(num_height + 1):
        for jdx in range(num_width + 1):
            verts.append(
                Vertex(x=float(jdx) * delta_w, y=float(idx) * delta_h, id=count)
            )
            count += 1

    # Generate cells
    cells: list[Cell] = []
    for idx in range(num_height):
        for jdx in range(num_width):
            v0 = jdx + (num_width + 1) * idx
            v1 = v0 + 1
            v2 = jdx + (num_width + 1) * (idx + 1) + 1
            v3 = v2 - 1

            cells.append(Cell(type="quad", vertices=(v0, v1, v2, v3)))

    return Mesh(vertices=tuple(verts), cells=tuple(cells)).apply_transform(
        rect.transform
    )


def mesh_annulus(
    annulus: Annulus, num_radial: int = 2, num_circumferential: int = 8
) -> Mesh:

    angle_rad = annulus.angle * np.pi / 180

    rect_mesh = mesh_rectangle(
        Quad(
            width=angle_rad * annulus.outer_radius,
            height=annulus.outer_radius - annulus.inner_radius,
            transform=Transform(location=Point(0.0, annulus.inner_radius)),
        ),
        num_width=num_circumferential,
        num_height=num_radial,
    )
    radial_mesh = map_radial(rect_mesh, annulus.angle)

    if annulus.angle == 360:
        return close_mesh(radial_mesh)
    return radial_mesh


def mesh_circle(
    circle: Circle,
    boundary_frac: float = 0.5,
    num_radial: int = 2,
    num_circumferential: int = 8,
) -> Mesh:

    annulus_mesh = mesh_annulus(
        Annulus(outer_radius=circle.radius, inner_radius=circle.radius * boundary_frac),
        num_radial=num_radial,
        num_circumferential=num_circumferential,
    )

    inner_radius = circle.radius * boundary_frac
    inner_mesh = mesh_rectangle(
        Quad(
            width=inner_radius,
            height=inner_radius,
            transform=Transform(
                location=Point(-inner_radius / 2.0, -inner_radius / 2.0)
            ),
        ),
        num_width=int(num_circumferential / 4),
        num_height=int(num_circumferential / 4),
    )

    merged = merge_meshes(annulus_mesh, inner_mesh)
    return merged


def mesh_cuboid(cuboid: Cuboid, elements_per_dim: int = 5) -> Mesh:

    verts = tuple(Vertex.from_point(p) for p in cuboid.points)

    cell_counts = (elements_per_dim, elements_per_dim, elements_per_dim)
    cells = (HexCell(vertices=tuple(range(len(verts))), cell_counts=cell_counts),)
    return Mesh(verts, cells)


def mesh_cuboids(
    cuboids: list[Cuboid], elements_per_dim: int = 5, merge_tolerance: float = 1.0e-4
) -> Mesh:

    verts: list = []
    block_vert_ids: list = []
    for cuboid in cuboids:
        vert_ids = []
        for p in cuboid.points:

            if not verts:
                verts.append(Vertex.from_point(p, 0))
                vert_ids.append(0)
                continue

            nearest_id = find_closest(verts, p)
            if verts[nearest_id].get_distance(p) <= merge_tolerance:
                vert_ids.append(nearest_id)
            else:
                end_id = len(verts)
                verts.append(Vertex.from_point(p, end_id))
                vert_ids.append(end_id)
        block_vert_ids.append(vert_ids)

    cell_counts = (elements_per_dim, elements_per_dim, elements_per_dim)
    cells = tuple(HexCell(tuple(b), cell_counts=cell_counts) for b in block_vert_ids)
    return Mesh(vertices=tuple(verts), cells=cells)


def mesh_cylinder(cylinder: Cylinder, boundary_frac: float = 0.66) -> Mesh:

    inner_cube_side = cylinder.diameter * boundary_frac / np.sqrt(2)
    outer_cube_x = cylinder.diameter / np.sqrt(2)
    outer_cube_z = cylinder.diameter * (1.0 - boundary_frac) / (2.0 * np.sqrt(2))

    cuboids = [
        Cuboid(
            Transform(Point(0.0, 0.0, -inner_cube_side / 2.0 - outer_cube_z / 2.0)),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(0.0, 0.0, inner_cube_side / 2.0 + outer_cube_z / 2.0),
                normal=Vector(0.0, 0.0, -1.0),
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(-outer_cube_x / 2.0, 0.0, 0.0), normal=Vector(-1.0, 0.0, 0.0)
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(
                Point(outer_cube_x / 2.0, 0.0, 0.0), normal=Vector(-1.0, 0.0, 0.0)
            ),
            width=outer_cube_x,
            height=cylinder.length,
            depth=outer_cube_z,
            top_width_scale=boundary_frac,
        ),
        Cuboid(
            Transform(Point(0.0, 0.0, 0.0)),
            width=inner_cube_side,
            height=cylinder.length,
            depth=inner_cube_side,
        ),
    ]

    mesh = mesh_cuboids(cuboids)

    """
    top_front_edge = mesh.get_closest_edge(
        Point(0.0, -cylinder.length / 2.0, cylinder.diameter + depth / 2.0)
    )
    top_front_arc = Point(
        0.0, -cylinder.length / 2.0, cylinder.diameter + depth / 2.0 + 0.15
    )

    # edges = (Edge(top_front_edge[0], top_front_edge[1], "arc", (top_front_arc,)),)
    """

    return Mesh(mesh.vertices, mesh.cells)
