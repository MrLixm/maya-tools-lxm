"""
author="Liam Collod<monsieurlixm@gmail.com>"
dependencies=[
    "python>3.8",
    "maya~=2023",
    "refrepath.py",
]
description="Repath references in multiple maya files at once."
"""
import argparse
import datetime
import logging
import sys
from pathlib import Path

from .batch import batch_directory
from . import c

logger = logging.getLogger(__name__)


def configure_logging(root_path: Path, level: int):
    """
    Configure the python logging system for the processing of the given directory.

    Args:
        root_path: path to an existing directory
        level: logging level to set the console logger to
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "{levelname: <7} | {asctime} [{name}][{funcName}] {message}", style="{"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if c.DRYRUN:
        return

    disk_handler_filename = (
        f"{c.name}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )
    disk_handler = logging.FileHandler(root_path / disk_handler_filename)
    disk_handler.setLevel(logging.DEBUG)
    disk_handler.setFormatter(formatter)
    root_logger.addHandler(disk_handler)
    return


def cli():
    """
    Command line argument for processing arg submitted by user.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Repath references in multiple maya files at once.\n"
            "References are repathed using the name of the submitted root directory as "
            "a common denominator. This is useful if only the left-most part of the "
            "path have to be updated."
        )
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Toggle logging at debug level.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not actually launch Maya and don't write any file to disk.",
    )
    parser.add_argument(
        "parse_root_path",
        help=(
            "Path to an existing disk to parse maya files from. If no other argument is "
            "specified, this will also be used as the new root directory for references repathing."
        ),
        type=str,
    )
    parser.add_argument(
        "--substitute_root_path",
        help="Directory path used as root for reference repathing.",
        type=str,
        default=None,
    )
    parsed = parser.parse_args()

    if parsed.dry_run:
        c.DRYRUN = True

    parse_root_path = Path(parsed.parse_root_path)
    if not parse_root_path.exists():
        raise FileNotFoundError(
            f"Given root_path doesn't exist on disk: {parse_root_path}"
        )

    substitute_root_path = parsed.substitute_root_path
    if not substitute_root_path:
        substitute_root_path = parse_root_path
    else:
        substitute_root_path = Path(substitute_root_path)
    if not substitute_root_path.exists():
        raise FileNotFoundError(
            f"Given substitute_root_path doesn't exist on disk: {substitute_root_path}"
        )

    logging_level = logging.DEBUG if parsed.debug else logging.INFO
    configure_logging(parse_root_path, logging_level)
    batch_directory(parse_root_path, substitute_root_path)


if __name__ == "__main__":
    cli()
