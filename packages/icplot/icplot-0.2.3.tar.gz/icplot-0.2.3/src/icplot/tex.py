"""
This module has functionality for publishing Tex documents
"""

import subprocess
from typing import NamedTuple
import shutil
import os
from pathlib import Path
import logging

from .image_utils import pdf_to_png

logger = logging.getLogger(__name__)


class TexBuildSettings(NamedTuple):
    """
    This holds settings for the Tex build
    """

    source: Path
    build_dir: Path
    output_dir: Path | None = None
    build_engine: str = "pdflatex"
    extra_flags: str = "-interaction=nonstopmode"
    output_png: bool = True
    clear_workdir: bool = True


def build_pdf(settings: TexBuildSettings, work_dir: Path):

    cmd = f"{settings.build_engine} {settings.extra_flags} {settings.source}"
    with open(work_dir / "stdout.txt", "w", encoding="utf-8") as f:
        subprocess.run(cmd, shell=True, check=True, cwd=work_dir, stdout=f, stderr=f)


def build_single(settings: TexBuildSettings):
    logger.info("Building source: %s", settings.source)

    # Make a working dir
    work_dir = settings.build_dir / settings.source.stem
    os.makedirs(work_dir, exist_ok=True)

    build_pdf(settings, work_dir)

    tex_path = work_dir / settings.source.name
    pdf_path = tex_path.parent / f"{tex_path.stem}.pdf"
    if settings.output_png:
        pdf_to_png(pdf_path)

    # If output dir is different to build dir copy final content there
    if settings.output_dir and settings.output_dir != work_dir:
        os.makedirs(settings.output_dir, exist_ok=True)
        shutil.copy(pdf_path, settings.output_dir)

        if settings.output_png:
            png_path = pdf_path.parent / f"{tex_path.stem}.png"
            shutil.copy(png_path, settings.output_dir)

        if settings.clear_workdir:
            shutil.rmtree(work_dir)


def build(settings: TexBuildSettings):
    if settings.source.is_dir():
        for tex_file in settings.source.glob("*.tex"):
            single_build = TexBuildSettings(
                tex_file,
                settings.build_dir,
                settings.output_dir,
                settings.build_engine,
            )
            build_single(single_build)
    else:
        build_single(settings)

    logger.info("Finished building sources")
