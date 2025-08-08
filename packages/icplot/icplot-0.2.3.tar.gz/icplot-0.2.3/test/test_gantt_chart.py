import os
import datetime
from pathlib import Path

from iccore.project import Milestone

from icplot.gantt import GanttChart


def test_gantt_chart():

    milestone0 = Milestone(
        title="My Milestone 0",
        description="Description of Milestone 0.",
        start_date=datetime.date(2024, 6, 30),
        due_date=datetime.date(2024, 7, 12),
    )

    milestone1 = Milestone(
        title="My Milestone 1",
        description="Description of Milestone 1.",
        start_date=datetime.date(2024, 7, 1),
        due_date=datetime.date(2024, 7, 15),
    )

    _ = GanttChart(milestones=[milestone0, milestone1])
