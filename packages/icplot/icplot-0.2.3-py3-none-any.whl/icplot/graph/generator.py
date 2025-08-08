from typing import Any, Callable
import os
from pathlib import Path

from pydantic import BaseModel

from iccore.serialization import read_yaml

from .plot import Plot
from .series import LinePlotSeries
from .matplotlib import render


class PlotConfig(BaseModel, frozen=True):

    series_attr: str
    x_attr: str
    plots: dict[str, Plot]
    colormap: Any


def make_plots(
    results: list[Any], config: PlotConfig, point_func: Callable
) -> list[Plot]:
    """
    For a set of results and a given plot config generate a list of
    plots.
    """

    # The instance attribute value for 'series_attr' is used to generate
    # a set of labels, one per plot series
    series_labels = set(getattr(r, config.series_attr) for r in results)

    plots: list[Plot] = []
    # Each 'y attribute' in the config corresponds to a 'plot' of this
    # attribute's values.
    for y_attr, plot_template in config.plots.items():

        series = []
        for label in series_labels:
            # Get results for this series
            label_results = [
                r for r in results if getattr(r, config.series_attr) == label
            ]

            # Use a user-provided 'point_func' to get the series 'x, y' points
            # from the results, given a 'x_attr, y_attr' pair
            all_points = [point_func(r, config.x_attr, y_attr) for r in label_results]
            points = sorted(
                [x for x in all_points if x is not None], key=lambda x: x[0]
            )
            x, y = [list(xy) for xy in zip(*points)]

            if label in config.colormap:
                series.append(
                    LinePlotSeries(
                        x=x,
                        y=y,
                        label=str(label),
                        highlight=True,
                        color=config.colormap[label],
                    )
                )
            else:
                series.append(LinePlotSeries(x=x, y=y, label=str(label)))
        plots.append(plot_template.copy(update={"name": y_attr, "series": series}))
    return plots


def plot(
    results: list[Any],
    config: PlotConfig,
    point_func: Callable,
    output_dir: Path = Path(os.getcwd()),
):
    """
    For a given set of results and plot config generate the
    corresponding plots and render them to files.
    """

    for p in make_plots(results, config, point_func):
        render(p, output_dir / f"{p.name}.svg")


def plot_file(config_path: Path, output_dir: Path):
    config = read_yaml(config_path)

    if ["plots"] not in config:
        return

    for p in [Plot(**p) for p in config["plots"]]:
        render(p, output_dir)
