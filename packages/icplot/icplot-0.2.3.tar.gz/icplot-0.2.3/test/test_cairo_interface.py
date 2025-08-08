import os
import shutil

from iccore.test_utils import get_test_output_dir

from icplot import cairo_interface
from icplot.scene import Scene, Rectangle, TextPath
from icplot.color import Color


def test_cairo_interface():

    scene_items = []
    rect = Rectangle(
        w=20,
        h=20,
        location=(10, 10),
        fill=Color.from_rgba(0.5, 0.5, 1, 0.5),
        stroke=Color.from_rgba(0.5, 0.0, 0.0, 0.5),
    )
    scene_items.append(rect)

    text = TextPath(content="Hello World", location=(5, 5))
    scene_items.append(text)

    output_dir = get_test_output_dir()
    os.makedirs(output_dir, exist_ok=True)

    scene = Scene(items=scene_items)
    cairo_interface.draw_svg(scene, output_dir / "output.svg")
    shutil.rmtree(output_dir)
