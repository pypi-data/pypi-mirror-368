from pathlib import Path
import os
import logging

from .mesh import Mesh

_HAS_VTK = True
try:
    import vtk
except ImportError as e:
    logging.getLogger(__name__).warning(
        "Disabling VTK stupport. Failed to load with: %s", e
    )
    _HAS_VTK = False


def has_vtk() -> bool:
    return _HAS_VTK


def write_unstructured_grid(mesh: Mesh, path: Path):

    if not has_vtk():
        raise RuntimeError("VTK support failed to load")

    os.makedirs(path.parent, exist_ok=True)

    points = vtk.vtkPoints()
    for v in mesh.vertices:
        points.InsertNextPoint(v.x, v.y, v.z)

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    for cell in mesh.cells:
        if cell.type == "quad":
            vtk_cell = vtk.vtkQuad()
        else:
            vtk_cell = vtk.vtkHexahedron()
        for idx, v_id in enumerate(cell.vertices):
            vtk_cell.GetPointIds().SetId(idx, v_id)
        grid.InsertNextCell(vtk_cell.GetCellType(), vtk_cell.GetPointIds())

    writer = vtk.vtkUnstructuredGridWriter()
    writer.SetInputData(grid)
    writer.SetFileName(path)
    writer.SetFileTypeToASCII()
    writer.Write()
