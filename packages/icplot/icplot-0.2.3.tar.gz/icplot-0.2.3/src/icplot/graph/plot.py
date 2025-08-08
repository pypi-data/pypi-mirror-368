"""
This module has content for generating plots
"""

import random
from pathlib import Path
import os

from pydantic import BaseModel

from iccore.data import Series
from iccore.data.series import convert_units

from icplot.color import ColorMap, Color
from icplot.graph import mpl, vtk

from .axis import PlotAxis
from .series import LinePlotSeries, ScatterPlotSeries, ImageSeries
from .plot_group import PlotGroupPublic, PlotSeriesPublic


class Plot(BaseModel, frozen=True):
    """
    A generic plot with optional axis ticks
    """

    title: str = ""
    name: str = ""
    x_axis: PlotAxis = PlotAxis()
    y_axes: list[PlotAxis] = [PlotAxis()]
    plot_type: str = ""
    line_series: list[LinePlotSeries] = []
    scatter_series: list[ScatterPlotSeries] = []
    image_series: list[ImageSeries] = []
    legend: str = "none"
    aspect: str = "auto"
    legend_fontsize: int = 10
    title_fontsize: int = 10

    @property
    def series(self):
        return self.line_series + self.scatter_series + self.image_series


class GridPlot(Plot, frozen=True):
    """
    Make a grid of plots
    """

    stride: int = 4
    size: tuple = (25, 20)
    data: list = []

    def get_series_indices(self, num_samples: int = 0):
        rows = num_samples // self.stride
        cols = num_samples // rows
        len_data = len(self.data)

        if num_samples == 0:
            indices = list(range(0, len_data))
        else:
            indices = [random.randint(0, len_data - 1) for _ in range(num_samples)]
        return rows, cols, indices

    def get_subplots(self, num_samples: int = 0):
        rows, cols, indices = self.get_series_indices(num_samples)

        subplots = []
        count = 1
        for index in indices:
            if num_samples > 0 and count == num_samples + 1:
                break
            if isinstance(self.data[index], list):
                for series in self.data[index]:
                    subplots.append(series)
                    count += 1
            else:
                subplots.append(self.data[index])
                count += 1
        return rows, cols, subplots


def get_series_colors(cmap: ColorMap, plot: Plot) -> list[Color]:

    count = 0
    num_colorable = len([s for s in plot.series if not s.highlight])
    colors = []
    for s in plot.series:
        if not s.highlight:
            color = cmap.get_color(count, num_colorable)
            count = count + 1
        else:
            color = s.color
        colors.append(color)
    return colors


def plot_series(
    path: Path,
    group: PlotGroupPublic,
    series: PlotSeriesPublic,
    data_series: Series,
):

    output_path = path / series.measurement.product_name

    os.makedirs(output_path, exist_ok=True)

    # Convert units
    if series.measurement.unit != series.unit:
        converted_data_series = convert_units(
            data_series,
            ((series.measurement.name, series.measurement.unit, series.unit),),
        )
    else:
        converted_data_series = data_series

    if "mpl" in group.formats:
        mpl.plot(output_path, group, series, converted_data_series)

    if "vtk" in group.formats and data_series.y:
        vtk.save(output_path, group, series, converted_data_series)
