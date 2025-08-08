"""
This module represents a gantt chard
"""

from datetime import datetime

from pydantic import BaseModel

from iccore.project import Milestone

from icplot.color import Color


class GanttChart(BaseModel, frozen=True):
    """
    A gantt chart
    """

    milestones: list[Milestone] = []
    title: str = ""
    start_date: datetime | None = None
    end_date: datetime | None = None
    bar_max_height: float = 0.1
    height: int = 100
    width: int = 500
    bar_color: Color = Color.from_rgba(0.7, 0, 0)
