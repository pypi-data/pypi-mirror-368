from datetime import datetime, timedelta
from icplot.graph.plot_group import (
    PlotGroupPublic,
    VideoConfig,
    ContourConfig,
    LineConfig,
)


def test_plot_group():
    now = datetime.utcnow()
    later = now + timedelta(hours=1)

    video = VideoConfig(fps=10, format="avi", active=False)
    contour = ContourConfig(show_grid=False, colormap="viridis", format="svg")
    line = LineConfig(format="pdf")

    group = PlotGroupPublic(
        start_datetime=now,
        end_datetime=later,
        video=video,
        contour=contour,
        line=line,
        formats=("mpl", "svg"),
        active=True,
        series=[],
    )

    assert group.has_date_range
    assert group.date_range == (now, later)
    assert group.video == video
    assert group.contour == contour
    assert group.line == line
    assert group.formats == ("mpl", "svg")
    assert group.active
