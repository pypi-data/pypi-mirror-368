import numpy as np

from .cell import Cell
from .vertex import Vertex
from .mesh import Mesh


def map_radial(mesh: Mesh, angle: float) -> Mesh:

    angle_rad = angle * np.pi / 180
    mapped_points = []
    bounds = mesh.get_bounds()

    for v in mesh.vertices:
        theta_frac = (v.x - bounds.xmin) / (bounds.xmax - bounds.xmin)
        x_mapped = v.y * np.cos(theta_frac * angle_rad) + bounds.xmin
        y_mapped = v.y * np.sin(theta_frac * angle_rad)
        mapped_points.append(Vertex(x=x_mapped, y=y_mapped, z=v.z, id=v.id))

    return Mesh(vertices=tuple(mapped_points), cells=mesh.cells)


def close_mesh(mesh: Mesh, tolerance: float = 1.0e-4) -> Mesh:

    # Find overlapping nodes
    overlaps: dict = {}

    for v0 in mesh.vertices:
        for v1 in mesh.vertices:
            if v0.id == v1.id:
                continue
            # Find the vert with the lowest id we overlap with
            if v0.get_vertex_distance(v1) < tolerance:
                overlaps[v0.id] = v1.id
                break

    # Build the new vertex list
    replacements: dict = {}
    reindex: dict = {}
    new_verts = []
    count = 0
    for v in mesh.vertices:
        # If we overlap a node with a lower index add that node to the replacement list
        if v.id in overlaps and v.id > overlaps[v.id]:
            replacements[v.id] = overlaps[v.id]
        else:
            reindex[v.id] = count
            new_verts.append(Vertex(x=v.x, y=v.y, z=v.z, id=count))
            count = count + 1

    # Build the new cell list
    new_cells = []
    for c in mesh.cells:
        updated_verts = []
        for v_id in c.vertices:
            if v_id in replacements:
                new_v = reindex[replacements[v_id]]
            else:
                new_v = reindex[v_id]
            updated_verts.append(new_v)
        new_cells.append(Cell(vertices=tuple(updated_verts), type=c.type))

    return Mesh(vertices=tuple(new_verts), cells=tuple(new_cells))


def merge_meshes(mesh0: Mesh, mesh1: Mesh, tolerance: float = 1.0e-4) -> Mesh:

    # Combine and reindex nodes
    nodes0 = {}
    nodes1 = {}

    new_nodes = []
    count = 0
    for v in mesh0.vertices:
        nodes0[v.id] = count
        new_nodes.append(Vertex(id=count, x=v.x, y=v.y, z=v.z))
        count += 1

    for v in mesh1.vertices:
        nodes1[v.id] = count
        new_nodes.append(Vertex(id=count, x=v.x, y=v.y, z=v.z))
        count += 1

    # Combine cells and use reindexed nodes
    new_cells = []
    for c in mesh0.cells:
        new_cells.append(
            Cell(type=c.type, vertices=tuple([nodes0[v] for v in c.vertices]))
        )
    for c in mesh1.cells:
        new_cells.append(
            Cell(type=c.type, vertices=tuple([nodes1[v] for v in c.vertices]))
        )

    combined = Mesh(cells=tuple(new_cells), vertices=tuple(new_nodes))

    return close_mesh(combined, tolerance)


def mesh_extrude(mesh: Mesh, depth: float, num_cells: int) -> Mesh:

    # Create new node layers
    delta = depth / num_cells
    new_nodes = []

    count = 0
    for idx in range(num_cells + 1):
        for v in mesh.vertices:
            new_nodes.append(Vertex(x=v.x, y=v.y, z=v.z + delta * float(idx), id=count))
            count += 1

    # Create new cells layers
    new_cells = []
    num_verts = len(mesh.vertices)
    for idx in range(num_cells):
        for c in mesh.cells:
            cell_verts = [v + idx * num_verts for v in c.vertices]
            cell_verts.extend([v + (idx + 1) * num_verts for v in c.vertices])
            new_cells.append(Cell(type="hex", vertices=tuple(cell_verts)))
    return Mesh(vertices=tuple(new_nodes), cells=tuple(new_cells))
