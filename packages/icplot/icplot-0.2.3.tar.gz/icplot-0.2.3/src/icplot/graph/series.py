"""
A data series in a plot
"""

import typing

from pydantic import BaseModel

from iccore.data import (
    ProductPublicWithMeasurements,
    MeasurementPublicWithUnits,
    Unit,
    UnitPublic,
)

from icplot.color import Color


class PlotSeriesBase(BaseModel, frozen=True):

    min_value: float | None = None
    max_value: float | None = None


class PlotSeriesCreate(PlotSeriesBase, frozen=True):

    measurement: str
    unit_name: str = ""

    @property
    def product(self) -> str:
        return self.measurement.split(".")[0]

    @property
    def base_measurement(self) -> str:
        return self.measurement.split(".")[1]


class PlotSeriesPublic(PlotSeriesBase, frozen=True):

    measurement: MeasurementPublicWithUnits
    unit: UnitPublic
    x: MeasurementPublicWithUnits | None
    y: MeasurementPublicWithUnits | None

    @property
    def has_limits(self) -> bool:
        return self.min_value is not None and self.max_value is not None

    @property
    def limits(self) -> tuple[float, float]:
        if self.max_value is None or self.min_value is None:
            raise ValueError("Attempted to access limits but none set")
        return self.min_value, self.max_value

    @classmethod
    def from_create(
        cls, create: PlotSeriesCreate, product: ProductPublicWithMeasurements
    ) -> "PlotSeriesPublic":

        measurement = product.get_measurement(create.base_measurement)

        if create.unit_name and create.unit_name != measurement.unit.name:
            unit = Unit.object(create.unit_name, "name", return_t=UnitPublic)
        else:
            unit = measurement.unit

        return PlotSeriesPublic(
            measurement=measurement,
            unit=unit,
            min_value=create.min_value,
            max_value=create.max_value,
            x=product.x,
            y=product.y,
        )


class PlotSeries(BaseModel, frozen=True):
    """
    A data series in a plot, such as a single line in a line-plot

    :param position_right: allows the series to be plotted on the right y-axis.
    :type position_right: bool, optional
    """

    label: str
    color: Color = Color()
    series_type: str = ""
    highlight: bool = False
    position_right: bool = False


class ImageSeries(PlotSeries, frozen=True):
    """
    A plot data series where the elements are images
    """

    data: typing.Any
    transform: typing.Any
    series_type: str = "image"


class LinePlotSeries(PlotSeries, frozen=True):
    """
    A plot series for line plots

    :param drawstyle: Naming comes from matplotlib API, allows for various square plots,
               default is a normal point to point line plot.
    :type drawstyle: str, optional
    """

    x: list
    y: list
    x_err: float | list[float] | list[list[float]] | None = None
    y_err: float | list[float] | list[list[float]] | None = None
    err_capsize: float = 2.0
    marker: str = "o"
    series_type: str = "line"
    drawstyle: str = "default"
    linestyle: str = "-"


class ScatterPlotSeries(PlotSeries, frozen=True):
    """
    Scatter type plot series
    """

    data: typing.Any
    series_type: str = "scatter"
