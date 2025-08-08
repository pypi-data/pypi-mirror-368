from pathlib import Path

import cairo

from .scene import Scene, Rectangle


def draw_rect(cr, rect: Rectangle):
    x0, y0 = rect.location
    x1 = rect.w
    y1 = rect.h
    cr.move_to(x0, y0)
    cr.line_to(x1, y0)
    cr.line_to(x1, y1)
    cr.line_to(x0, y1)
    cr.close_path()


def draw_shape(cr, shape):
    cr.save()
    if shape.shape_type == "rect":
        draw_rect(cr, shape)
    else:
        return
    cr.set_source_rgba(shape.fill.r, shape.fill.g, shape.fill.b, shape.fill.a)
    cr.fill_preserve()
    if shape.stroke is not None:
        cr.set_source_rgba(
            shape.stroke.r, shape.stroke.g, shape.stroke.b, shape.stroke.a
        )
        cr.set_line_width(shape.stroke_thickness)
        cr.stroke()

    cr.restore()


def draw_text(cr, text):
    cr.save()

    cr.select_font_face(text.font.family)
    cr.set_font_size(text.font.size)
    cr.move_to(text.location[0], text.location[1])
    cr.show_text(text.content)

    cr.restore()


def draw_scene(cr, scene: Scene):
    for item in scene.items:
        if item.item_type == "shape":
            draw_shape(cr, item)
        elif item.item_type == "text":
            draw_text(cr, item)


def draw_svg(scene: Scene, path: Path):
    with cairo.SVGSurface(path, scene.size[0], scene.size[1]) as surface:
        cr = cairo.Context(surface)
        draw_scene(cr, scene)
