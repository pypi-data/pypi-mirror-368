import shutil
from pathlib import Path

from iccore.test_utils import get_test_data_dir, get_test_output_dir

from icplot import mermaid


def test_mermaid():

    if not mermaid.has_mermaid():
        return

    # Pass in the browser config so we can also run headless
    # on the CI
    browser_config = Path(__file__).parent.parent / "infra/puppeteer-config.json"

    output_dir = get_test_output_dir()
    source = get_test_data_dir() / "test.mmd"

    mermaid.convert(source, output_dir, browser_config)
    assert Path(output_dir / "test.png").exists()

    shutil.rmtree(output_dir)
