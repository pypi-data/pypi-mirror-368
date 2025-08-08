from pathlib import Path

from icplot.graph import Plot, LinePlotSeries, PlotAxis, Range
from icplot.graph import matplotlib


def test_line_plot():

    data = [([0, 5, 10], [1, 2, 3]), ([0, 5, 10], [3, 6, 9]), ([0, 5, 10], [4, 8, 12])]

    series = []
    for idx, [x, y] in enumerate(data):
        series_config = {"label": f"Series {idx}", "x": x, "y": y}
        series.append(LinePlotSeries(**series_config))

    x_axis_config = {
        "label": "x_axis",
        "ticks": Range(lower=0, upper=11, step=2),
        "scale": "linear",
        "text_fontsize": 10,
        "tick_fontsize": 10,
        "max_ticks": 0,
        "limits": {"bottom": 0},
    }
    x_axis = PlotAxis(**x_axis_config)
    y_axis_config = {
        "label": "y_axis",
        "ticks": Range(lower=0, upper=16, step=5),
        "scale": "linear",
        "text_fontsize": 10,
        "tick_fontsize": 10,
        "max_ticks": 0,
        "limits": {"upper": 15},
    }
    y_axis = PlotAxis(**y_axis_config)
    plot_config = {
        "title": "Title",
        "name": "test",
        "x_axis": x_axis,
        "y_axes": [y_axis],
        "plot_type": "",
        "line_series": series,
        "legend": "upper left",
        "aspect": "auto",
        "legend_fontsize": 10,
        "title_fontsize": 10,
    }

    plot = Plot(**plot_config)

    output_path = Path() / "output.svg"
    matplotlib.render(plot, output_path)

    assert output_path.exists()
    output_path.unlink()


def test_error_line_plot():
    pass


def test_twin_line_plot():
    pass
