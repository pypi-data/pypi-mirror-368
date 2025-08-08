from pathlib import Path
import logging

import numpy as np

from iccore.data import Series

from .plot_group import PlotGroupPublic, PlotSeriesPublic

_HAS_VTK = True
try:
    import vtk
    from vtk.util import numpy_support
except ImportError as e:
    logging.getLogger(__name__).warning(
        "Disabling VTK stupport. Failed to load with: %s", e
    )
    _HAS_VTK = False


def has_vtk() -> bool:
    return _HAS_VTK


def to_grid(series: PlotSeriesPublic, data_series: Series):

    if not has_vtk():
        raise RuntimeError("VTK support failed to load")

    if not series.x:
        raise ValueError("Attempting to plot a series with no data")

    if not series.y:
        raise ValueError("Expected 2d series for grid plot.")

    x = data_series.get_x_array().data
    y = data_series.get_y_array().data

    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions([len(x), len(y), 1])

    points = vtk.vtkPoints()
    count = 0

    x0 = x[0]
    for y_pt in y:
        for x_pt in x:
            delta_x = x_pt.timestamp() - x0.timestamp()
            points.InsertPoint(count, [delta_x, y_pt, 0])
            count += 1
    grid.SetPoints(points)

    for v in data_series.values:
        scalars = numpy_support.numpy_to_vtk(
            num_array=np.array(v.data[:]).flatten(order="F"),
            deep=True,
            array_type=vtk.VTK_FLOAT,
        )
        scalars.SetName(series.measurement.name)
        grid.GetPointData().AddArray(scalars)
    return grid


def save(
    path: Path,
    group: PlotGroupPublic,
    series: PlotSeriesPublic,
    data_series: Series,
    filename: str = "series",
):

    if not has_vtk():
        raise RuntimeError("VTK support failed to load")

    grid = to_grid(series, data_series)

    writer = vtk.vtkStructuredGridWriter()
    writer.SetFileName(path / f"{filename}.vtk")
    writer.SetInputData(grid)
    writer.Update()
    writer.Write()
