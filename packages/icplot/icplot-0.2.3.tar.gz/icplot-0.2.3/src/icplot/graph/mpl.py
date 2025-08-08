"""
Module to support plotting with matplotlib
"""

import os
from pathlib import Path
import shutil

import numpy as np
import matplotlib.pyplot as plt

from iccore.data.measurement import MeasurementPublicWithUnits
from iccore.data.units import to_date_str
from iccore.data import Series, UnitPublic

from .plot_group import PlotGroupPublic
from .series import PlotSeriesPublic
from .video import images_to_video


def get_axis_label(
    measurement: MeasurementPublicWithUnits, unit: UnitPublic | None = None
) -> str:

    if unit:
        resolved_unit = unit
    else:
        resolved_unit = measurement.unit

    if measurement.name == "time":
        return f"{measurement.get_long_name()} (UTC)"

    if measurement.unit.symbol:
        return f"{measurement.get_long_name()} ({resolved_unit.symbol})"

    return measurement.long_name


def get_grid(series: Series):

    if not series.x or not series.y:
        raise RuntimeError("Series missing expected data")

    return np.meshgrid(series.get_x_array().data, series.get_y_array().data)


def save_plot(fig, path: Path, filename: str, file_prefix: str = ""):
    plt.tight_layout()
    prefix = f"{file_prefix}_" if file_prefix else ""
    os.makedirs(path, exist_ok=True)
    plt.savefig(path / f"{prefix}{filename}")
    plt.clf()
    plt.close(fig)


def get_date_suffix(group: PlotGroupPublic) -> str:
    if not group.has_date_range:
        return ""
    start, end = group.date_range
    return f"_FROM_{to_date_str(start)}_TO_{to_date_str(end)}"


def plot_2d(
    path: Path, group: PlotGroupPublic, series: PlotSeriesPublic, data_series: Series
):
    """
    Generate a contour plot for the provided quantity
    """

    if not data_series.x or not series.x:
        raise RuntimeError("Expected series with an x quantity")

    if not data_series.y or not series.y:
        raise RuntimeError("Expected series with a y quantity.")

    x, y = get_grid(data_series)

    array = data_series.get_array(series.measurement.name)

    fig, ax = plt.subplots()

    ax.set_xlabel(get_axis_label(series.x))
    ax.set_ylabel(get_axis_label(series.y))

    if group.has_date_range:
        ax.set_xlim(group.date_range)  # type: ignore
    fig.autofmt_xdate()

    if group.contour.show_grid:
        ax.grid(c="k", ls="-", alpha=0.3)

    if False and array.quantity.has_limits:
        cs = ax.contourf(
            x,
            y,
            np.clip(array.data.T, array.quantity.limits[0], array.quantity.limits[1]),
            cmap=group.contour.colormap,
        )
    else:
        cs = ax.contourf(x, y, np.array(array.data).T, cmap=group.contour.colormap)

    cbar = fig.colorbar(cs)
    cbar.ax.set_ylabel(get_axis_label(series.measurement, series.unit))

    date_str = get_date_suffix(group)
    save_plot(fig, path, f"{series.measurement.name}{date_str}.{group.contour.format}")


def plot_1d(
    path: Path, group: PlotGroupPublic, series: PlotSeriesPublic, data_series: Series
):
    """
    Generate a line plot for the provided quantity
    """

    if not data_series.x or not series.x:
        raise RuntimeError("Attempted to plot series without x data")

    fig, ax = plt.subplots()
    ax.set_xlabel(get_axis_label(series.x))
    ax.set_ylabel(get_axis_label(series.measurement, series.unit))

    if group.has_date_range:
        ax.set_xlim(group.date_range)  # type: ignore
    fig.autofmt_xdate()

    if series.has_limits:
        ax.set_ylim(series.limits)  # type: ignore

    x = data_series.get_array(series.x.name).data
    y = data_series.get_array(series.measurement.name).data
    ax.plot(x, y)

    date_str = get_date_suffix(group)
    save_plot(
        fig,
        path,
        f"{series.measurement.name}{date_str}.{group.line.format}",
    )


def plot_array(path: Path, series: PlotSeriesPublic, data_series: Series):
    """
    Plot an array for a single series x value. Useful for
    time series video frames.
    """

    array = data_series.get_array(series.measurement.name)

    if not data_series.x or not data_series.y or not series.y:
        raise RuntimeError("Attempted to plot series with missing data")

    for idx, (x, values) in enumerate(
        zip(data_series.get_array(data_series.x).data, array.data)
    ):
        fig, ax = plt.subplots()

        ax.set_title(x)
        ax.set_xlabel(get_axis_label(series.measurement, series.unit))
        ax.set_ylabel(get_axis_label(series.y))

        if series.has_limits:
            ax.set_xlim(series.limits)  # type: ignore

        ax.plot(values, data_series.get_array(data_series.y).data)

        save_plot(fig, path / f"{series.measurement.name}", f"{idx}.png")


def make_video(
    path: Path, group: PlotGroupPublic, series: PlotSeriesPublic, data_series: Series
):

    plot_array(path, series, data_series)

    if not group.video:
        return

    images_to_video(
        path / f"{series.measurement.name}",
        path,
        f"{series.measurement.name}{get_date_suffix(group)}",
        fps=group.video.fps,
        video_format=group.video.format,
    )
    shutil.rmtree(path / f"{series.measurement.name}")


def plot(
    path: Path, group: PlotGroupPublic, series: PlotSeriesPublic, data_series: Series
):
    """
    Handle plotting 1-d and 2-d time series and videos for the given quantity
    """

    if data_series.y:
        plot_2d(path, group, series, data_series)

        if group.video and group.video.active:
            make_video(path, group, series, data_series)
        return

    plot_1d(path, group, series, data_series)
