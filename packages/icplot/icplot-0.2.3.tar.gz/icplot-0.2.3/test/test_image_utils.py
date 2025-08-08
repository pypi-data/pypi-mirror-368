import os
from pathlib import Path

from icplot.image_utils import svg_to_png, svg_to_pdf


def get_test_data_dir():
    return Path(__file__).parent / "data"


def test_convert_svg():

    source = get_test_data_dir() / "test.svg"

    png_out = Path(os.getcwd()) / "out.png"
    svg_to_png(source, png_out)
    png_out.unlink()

    pdf_out = Path(os.getcwd()) / "out.pdf"
    svg_to_pdf(source, pdf_out)
    pdf_out.unlink()
