"""
This module has a plot's axis
"""

from pydantic import BaseModel


class Range(BaseModel, frozen=True):
    """
    This is a sequence of numbers specified by lower and upper
    bounds and a step size. Eg (1, 5, 1) gives: [1, 2, 3, 4]
    """

    lower: int
    upper: int
    step: int

    def eval(self) -> list:
        return list(range(self.lower, self.upper, self.step))


class PlotAxis(BaseModel, frozen=True):
    """
    This is a plot's axis

    :param str label: The axis label
    :param Range | None: A specification for tick marks
    """

    label: str = ""
    ticks: Range | list[int] | None = None
    scale: str = "linear"
    text_fontsize: int = 10
    tick_fontsize: int = 10
    max_ticks: int = 0
    limits: dict = {}

    @property
    def resolved_ticks(self) -> list:
        if self.ticks:
            if isinstance(self.ticks, Range):
                return self.ticks.eval()
            return self.ticks
        return []
