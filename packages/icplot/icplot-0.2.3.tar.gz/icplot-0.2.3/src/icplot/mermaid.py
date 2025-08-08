"""
Interface for generating mermaid plots.

Mermaid must already be set up on the system, eg. via the npm ecosystem.
"""

import subprocess
import shutil
import os
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def has_mermaid() -> bool:
    """
    True if the mermaid cli is found in the environment
    """

    return bool(shutil.which("mmdc"))


def convert(input_path: Path, work_dir: Path, browser_config: Path | None = None):

    if not has_mermaid():
        raise RuntimeError("Mermaid CLI 'mmdc' not found in path.")

    os.makedirs(work_dir, exist_ok=True)

    output_path = work_dir / f"{input_path.stem}.png"

    logger.info("Converting: %s to %s", input_path, output_path)

    cmd = f"mmdc -i {input_path} -o {output_path}"
    if browser_config:
        cmd += f" -p {browser_config}"
    subprocess.run(cmd, shell=True, check=True)
