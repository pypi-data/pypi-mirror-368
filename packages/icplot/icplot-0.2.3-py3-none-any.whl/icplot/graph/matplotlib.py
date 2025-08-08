from pathlib import Path
import logging
from typing import cast

logging.getLogger("matplotlib").setLevel(logging.WARNING)
import matplotlib as mpl  # NOQA

default_backend = mpl.get_backend()
mpl.use("Agg")
import matplotlib.pyplot as plt  # NOQA
from matplotlib.ticker import FuncFormatter  # NOQA

from icplot.color import ColorMap, Color  # NOQA
from .series import PlotSeries, LinePlotSeries, ScatterPlotSeries, ImageSeries  # NOQA
from .plot import Plot, GridPlot, get_series_colors  # NOQA
from .axis import PlotAxis  # NOQA


class MatplotlibColorMap(ColorMap):
    """
    A matplotlib based colormap
    """

    def __init__(self, label: str):
        super().__init__(label, mpl.colormaps[label])


def str_exact_values_formatter(x, pos):
    """
    When using log scale, axis ticks come out as scientific notation by default,
    then when using plain formatter values less than 1 come out as 0. A way around
    this is this custom formatter.
    """
    return str(int(x)) if x.is_integer else str(x)


def _set_legend_decorations(axs, plot):
    if plot.legend.lower() != "none":
        if len(axs) == 1:
            axs[0].legend(loc=plot.legend, frameon=False, fontsize=plot.legend_fontsize)
        else:
            axs[0].legend(
                loc="upper left", frameon=False, fontsize=plot.legend_fontsize
            )
            axs[1].legend(
                loc="upper right", frameon=False, fontsize=plot.legend_fontsize
            )


def _set_x_axis_decorations(x_axis: PlotAxis, ax):
    ax.set_yscale(x_axis.scale)
    ax.tick_params(axis="x", labelsize=x_axis.tick_fontsize)
    if x_axis.label:
        ax.set_xlabel(x_axis.label, fontsize=x_axis.text_fontsize)
    if x_axis.ticks:
        ax.set_xticks(x_axis.resolved_ticks)
    if x_axis.max_ticks:
        ax.xaxis.set_major_locator(plt.MaxNLocator(x_axis.max_ticks))
    for key, item in x_axis.limits.items():
        if key == "left" or key == "xmin":
            ax.set_xlim(xmin=item)
        elif key == "right" or key == "xmax":
            ax.set_xlim(xmax=item)


def _set_y_axes_decorations(y_axes: list[PlotAxis], axs):
    for idx, y_axis in enumerate(y_axes):
        axs[idx].set_yscale(y_axis.scale)
        axs[idx].tick_params(axis="y", labelsize=y_axis.tick_fontsize)
        if y_axis.scale == "log":
            formatter = FuncFormatter(str_exact_values_formatter)
            axs[idx].yaxis.set_major_formatter(formatter)
        if y_axis.label:
            axs[idx].set_ylabel(y_axis.label, fontsize=y_axis.text_fontsize)
        if y_axis.ticks:
            axs[idx].set_yticks(y_axis.resolved_ticks)
        if y_axis.max_ticks:
            axs[idx].yaxis.set_major_locator(plt.MaxNLocator(y_axis.max_ticks))
        for key, item in y_axis.limits.items():
            if key in ("bottom", "ymin"):
                axs[idx].set_ylim(ymin=item)
            elif key in ("top", "ymax"):
                axs[idx].set_ylim(ymax=item)


def _set_decorations(axs, plot: Plot):
    _set_legend_decorations(axs, plot)
    _set_x_axis_decorations(plot.x_axis, axs[0])
    _set_y_axes_decorations(plot.y_axes, axs)
    if plot.title:
        axs[0].set_title(plot.title, fontsize=plot.title_fontsize)
    axs[0].set_aspect(plot.aspect)


def _plot_line(axs, series: LinePlotSeries, color: Color | None):
    if not series.position_right:
        ax = axs[0]
    else:
        ax = axs[1]

    if color:
        render_color: list | None = color.as_list()
    else:
        render_color = None
    ax.errorbar(
        series.x,
        series.y,
        xerr=series.x_err,
        yerr=series.y_err,
        capsize=series.err_capsize,
        label=series.label,
        color=render_color,
        marker=series.marker,
        drawstyle=series.drawstyle,
        linestyle=series.linestyle,
    )


def _plot_scatter(ax, series: ScatterPlotSeries, color: Color | None):

    if color:
        render_color: list | None = series.color.as_list()
    else:
        render_color = None

    ax.scatter(series.data, label=series.label, color=render_color)


def _plot_image(ax, series: ImageSeries):
    ax.imshow(series.data)
    ax.axis("off")


def _plot_series(axs, series: PlotSeries, color: Color | None = None):
    ax = axs[0]
    if series.series_type == "line":
        _plot_line(axs, cast(LinePlotSeries, series), color)
    elif series.series_type == "scatter":
        _plot_scatter(ax, cast(ScatterPlotSeries, series), color)
    elif series.series_type == "image":
        _plot_image(ax, cast(ImageSeries, series))


def _render(fig, path: Path | None = None):
    if path:
        fig.savefig(path)
    else:
        plt.switch_backend(default_backend)
        fig.show()
        plt.switch_backend("Agg")


def render(
    plot: Plot, path: Path | None = None, cmap=MatplotlibColorMap("gist_rainbow")
):

    colors = get_series_colors(cmap, plot)

    fig, ax = plt.subplots()
    axs = [ax]
    if len(plot.y_axes) > 1:
        axs.append(ax.twinx())

    for series, color in zip(plot.series, colors):
        _plot_series(axs, series, color)

    _set_decorations(axs, plot)

    _render(fig, path)


def render_grid(
    plot: GridPlot,
    path: Path | None = None,
    num_samples: int = 0,
):
    rows, cols, series = plot.get_subplots(num_samples)
    fig, axs = plt.subplots(rows, cols)

    for ax, series_item in zip(axs, series):
        _plot_series(ax, series_item)

    _render(fig, path)
