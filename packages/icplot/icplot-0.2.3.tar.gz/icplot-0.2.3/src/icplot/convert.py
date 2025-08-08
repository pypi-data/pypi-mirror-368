"""
Module supporting conversion between various formats
"""

import logging
import os
from pathlib import Path

from icplot import tex, mermaid
from icplot.tex import TexBuildSettings
from icplot.image_utils import pdf_to_png, svg_to_pdf, svg_to_png


logger = logging.getLogger(__name__)


def convert(
    source: Path, target: Path, build_dir: Path, extra_config: Path | None = None
):
    """
    Convert the file at source outputing at target and using
    the source and target file extensions as format hints.

    Some conversions require a build_dir for intermediate or
    temporary output
    """

    logger.info("Converting between %s and %s", source, target)

    if source.suffix == ".pdf":
        pdf_to_png(source, target)
    elif source.suffix == ".svg":
        if target:
            if target.suffix == ".png":
                svg_to_png(source, target)
            elif target.suffix == ".pdf":
                svg_to_pdf(source, target)
        else:
            svg_to_png(source)
    elif source.suffix == ".tex":
        if not target:
            target = Path(os.getcwd())
        settings = TexBuildSettings(source, build_dir, target)
        tex.build(settings)
    elif source.suffix == ".mmd":
        if not target:
            target = Path(os.getcwd())
        settings = TexBuildSettings(source, build_dir, target)
        mermaid.convert(source, target, extra_config)

    logger.info("Finished conversion")
