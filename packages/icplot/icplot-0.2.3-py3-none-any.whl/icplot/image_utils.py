"""
This module has functions for converting between image
formats
"""

import logging
import os
from pathlib import Path

_HAS_WAND = True
try:
    from wand.image import Image
    from wand.color import Color
except ImportError as e:
    logging.getLogger(__name__).warning(
        "Disabling Wand stupport. Failed to load with: %s", e
    )
    _HAS_WAND = False

_HAS_CAIRO_SVG = True
try:
    import cairosvg
except ImportError as e:
    logging.getLogger(__name__).warning(
        "Disabling CairoSVG stupport. Failed to load with: %s", e
    )
    _HAS_CAIRO_SVG = False

logger = logging.getLogger(__name__)


def has_wand() -> bool:
    return _HAS_WAND


def has_cairo_svg() -> bool:
    return _HAS_CAIRO_SVG


def _get_out_filename(source: Path, target: Path | None, extension: str) -> Path:
    if target:
        return target
    return source.parent / f"{source.stem}.{extension}"


def pdf_to_png(source: Path, target: Path | None = None, resolution: int = 300):
    """
    Convert a pdf to png with white background
    """

    if not has_wand():
        raise RuntimeError("Loading Wand failed - no pdf to png support")

    outfile = _get_out_filename(source, target, "png")
    os.makedirs(outfile.parent, exist_ok=True)

    with Image(filename=source, resolution=resolution) as img:
        img.format = "png"
        img.background_color = Color("white")
        img.alpha_channel = "remove"
        img.save(filename=outfile)


def svg_to_png(source: Path, target: Path | None = None):
    """
    Convert an svg to png
    """

    if not has_cairo_svg():
        raise RuntimeError("Loading Cairosvg failed - no svg to png support")

    outfile = _get_out_filename(source, target, "png")
    os.makedirs(outfile.parent, exist_ok=True)
    cairosvg.svg2png(url=str(source), write_to=str(outfile))


def svg_to_pdf(source: Path, target: Path | None = None):
    """
    Convert an svg to pdf
    """

    if not has_cairo_svg():
        raise RuntimeError("Loading Cairosvg failed - no svg to pdf support")

    outfile = _get_out_filename(source, target, "pdf")
    os.makedirs(outfile.parent, exist_ok=True)
    cairosvg.svg2pdf(url=str(source), write_to=str(outfile))
