import shutil
from pathlib import Path

from iccore.test_utils import get_test_data_dir, get_test_output_dir

from icplot import tex
from icplot.tex import TexBuildSettings


def test_tex():

    data_dir = get_test_data_dir()
    build_dir = get_test_output_dir()
    source = data_dir / "test.tex"

    settings = TexBuildSettings(source, build_dir, build_dir)

    tex.build(settings)

    assert Path(build_dir / "test.pdf").exists()
    assert Path(build_dir / "test.png").exists()

    shutil.rmtree(build_dir)
