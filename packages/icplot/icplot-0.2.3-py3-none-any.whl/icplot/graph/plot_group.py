"""
Module to handle generation of plots
"""

from datetime import datetime
from dataclasses import dataclass

from pydantic import BaseModel

from .series import PlotSeriesCreate, PlotSeriesPublic


@dataclass(frozen=True)
class VideoConfig:
    """
    Representation of a video
    """

    fps: int = 5
    format: str = "mp4"
    active: bool = True


@dataclass(frozen=True)
class ContourConfig:
    """
    Representation of a contour plot
    """

    show_grid: bool = True
    colormap: str = "rainbow"
    format: str = "png"


@dataclass(frozen=True)
class LineConfig:
    """
    Representatino of a line plot
    """

    format: str = "png"


class PlotGroupBase(BaseModel, frozen=True):

    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    video: VideoConfig | None = None
    contour: ContourConfig = ContourConfig()
    line: LineConfig = LineConfig()
    formats: tuple[str, ...] = ("mpl",)
    active: bool = True

    @property
    def has_date_range(self) -> bool:
        return self.start_datetime is not None and self.end_datetime is not None

    @property
    def date_range(self) -> tuple[datetime, datetime]:

        if self.start_datetime is None or self.end_datetime is None:
            raise ValueError("Requested data range but none set")

        return self.start_datetime, self.end_datetime


class PlotGroupCreate(PlotGroupBase, frozen=True):
    """
    A group of plots to be generated, one per quantity.
    """

    series: list[PlotSeriesCreate] = []


class PlotGroupPublic(PlotGroupBase, frozen=True):
    """
    A group of plots to be generated, one per quantity.
    """

    series: list[PlotSeriesPublic] = []
