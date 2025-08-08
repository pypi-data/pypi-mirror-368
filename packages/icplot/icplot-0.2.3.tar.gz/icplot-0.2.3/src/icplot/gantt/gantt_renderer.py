from iccore.project import Milestone
from icplot.scene import Scene, SceneItem, Rectangle

from .gantt import GanttChart


def _render_milestone(
    gantt: GanttChart, milestone: Milestone, chart_range, yloc
) -> SceneItem:
    # chart_delta = chart_range[1] - chart_range[0]
    chart_delta = 0
    start_delta = milestone.start_date - chart_range[0]
    # milestone_delta = milestone.due_date - milestone.start_date
    milestone_delta = 0

    start_frac = float(start_delta / chart_delta)
    milestone_frac = float(milestone_delta / chart_delta)

    w = milestone_frac * gantt.width
    h = gantt.bar_max_height * gantt.height
    x = start_frac * gantt.width
    y = yloc

    rect = Rectangle(w=w, h=h, location=(x, y), fill=gantt.bar_color)
    return rect


def _render_milestones(gantt: GanttChart) -> list[SceneItem]:

    scene_items: list = []
    if not gantt.milestones:
        return scene_items

    milestones = gantt.milestones
    # milestones.sort(key=lambda x: x.start_date, reverse=True)

    start_date = gantt.start_date
    end_date = gantt.end_date
    if not start_date:
        start_date = milestones[0].start_date

    # if not end_date:
    #    end_date = max(m.due_date for m in milestones)

    chart_range = (start_date, end_date)
    yloc = 0.0
    bar_height = gantt.bar_max_height * gantt.height

    for milestone in milestones:
        item = _render_milestone(gantt, milestone, chart_range, yloc)
        scene_items.append(item)
        yloc += bar_height
    return scene_items


def render(gantt: GanttChart) -> Scene:
    scene = Scene()
    items = _render_milestones(gantt)
    scene.items.extend(items)
    return scene
