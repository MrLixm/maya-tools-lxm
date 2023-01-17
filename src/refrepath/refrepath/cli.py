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
from .utils import ColoredFormatter

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
    formatter = ColoredFormatter(
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
        prog=c.name,
        description=(
            "Repath references in multiple maya files at once.\n"
            "References are repathed using the name of the submitted root directory as "
            "a common denominator. This is useful if only the left-most part of the "
            "path have to be updated."
        ),
    )
    parser.add_argument("--version", action="version", version=c.__version__)
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
        "maya_file_dir",
        help=(
            "Path to an existing disk to parse maya files from. If no other argument is "
            "specified, this will also be used as the new root directory for references repathing."
        ),
        type=str,
    )
    parser.add_argument(
        "--new_root_dir",
        help="Directory path used as root for reference repathing.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--denominator",
        help="Part of the new_root_dir path used to split the initial reference path.",
        type=str,
        default=None,
    )
    parsed = parser.parse_args()

    if parsed.dry_run:
        c.DRYRUN = True

    maya_file_dir = Path(parsed.maya_file_dir)
    if not maya_file_dir.exists():
        raise FileNotFoundError(
            f"Given maya_file_dir doesn't exist on disk: {maya_file_dir}"
        )

    logging_level = logging.DEBUG if parsed.debug else logging.INFO
    configure_logging(maya_file_dir, logging_level)

    new_root_dir = parsed.new_root_dir
    if not new_root_dir:
        new_root_dir = maya_file_dir
    else:
        new_root_dir = Path(new_root_dir)
    if not new_root_dir.exists():
        raise FileNotFoundError(
            f"Given new_root_dir doesn't exist on disk: {new_root_dir}"
        )

    denominator = parsed.denominator
    if not denominator:
        denominator = new_root_dir.name

    denominator = Path(denominator)

    if not c.Env.get(c.Env.maya_batch):
        logger.warning("! missing MAYA_BATCH_PATH env var. Using default value.")
    maya_batch = c.Env.get(
        c.Env.maya_batch,
        r"C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe",
    )

    batch_directory(
        maya_files_dir=maya_file_dir,
        new_root_dir=new_root_dir,
        denominator=denominator,
        maya_batch_path=maya_batch,
    )


if __name__ == "__main__":
    cli()
