from pathlib import Path

from .gantt import GanttChart


def render(gantt: GanttChart) -> str:

    with open(Path(__file__).parent / "pgfgantt.tex", "r", encoding="utf-8") as f:
        template = f.read()

    if gantt.title:
        title_str = f"\\title{{{gantt.title}}}"
        template.replace("%%TITLE%%", title_str)

    return template
