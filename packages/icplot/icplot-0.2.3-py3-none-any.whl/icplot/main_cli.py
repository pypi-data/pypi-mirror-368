#!/usr/bin/env python3
import argparse
import logging
from pathlib import Path
import os

from iccore.cli_utils import launch_common

import icplot
import icplot.graph

logger = logging.getLogger(__name__)


def convert_cli(args):
    launch_common(args)

    if args.target:
        target = Path(args.target).resolve()
    else:
        target = None

    if args.extra_config:
        extra_config = Path(args.extra_config).resolve()
    else:
        extra_config = None

    icplot.convert(args.source.resolve(), target, args.buid_dir.resolve(), extra_config)


def plot_cli(args):

    launch_common(args)

    icplot.graph.plot_file(args.config.resolve(), args.output_dir.resolve())


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    convert_parser = subparsers.add_parser("convert")
    convert_parser.add_argument(
        "--source",
        type=Path,
        help="Path to file to be converted from",
    )
    convert_parser.add_argument(
        "--target",
        type=str,
        default="",
        help="Path to file to be converted to",
    )
    convert_parser.add_argument(
        "--build_dir",
        default=Path(os.getcwd()) / "_build/tikz",
        help="Path for build output",
    )
    convert_parser.add_argument(
        "--extra_config",
        type=str,
        default="",
        help="Extra config for third party tooling, e.g. puppeteer for mermaid",
    )
    convert_parser.set_defaults(func=convert_cli)

    plot_parser = subparsers.add_parser("plot")
    plot_parser.add_argument("--config", type=Path, help="Path to the plot config")
    plot_parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the plot output directory",
    )
    plot_parser.set_defaults(func=plot_cli)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_cli()
