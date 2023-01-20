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
import fnmatch
import logging
import re
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

    base_format = "{levelname: <7} | {asctime} [{name}][{funcName}] {message}"

    formatter = logging.Formatter(base_format, style="{")
    colored_formatter = ColoredFormatter(base_format, style="{")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(colored_formatter)
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
        "search",
        help="Part of the reference's path to replace. A fnmatch-compatible pattern.",
        type=str,
    )
    parser.add_argument(
        "replace",
        help=(
            "Partial path to swap with the result of the search. "
            'You can use "::use_maya_file_dir" if it is the same.'
        ),
        type=str,
    )
    parser.add_argument(
        "--zfill",
        help="number of zero for padding on file names increment.",
        type=int,
        default=c.PATH_ZFILL,
    )
    parser.add_argument(
        "--backup_suffix",
        help='str to include at the end of the name of backup files. ex: ".original"',
        type=str,
        default=c.PATH_BACKUP_SUFFIX,
    )
    parser.add_argument(
        "--ignore_backups",
        action="store_true",
        help="Do not process maya files that are considered backups from a previous repath.",
    )

    parsed = parser.parse_args()

    if parsed.dry_run:
        c.DRYRUN = True

    if parsed.backup_suffix is not None:
        c.PATH_BACKUP_SUFFIX = parsed.backup_suffix

    if parsed.zfill is not None:
        c.PATH_ZFILL = parsed.zfill

    maya_file_dir = Path(parsed.maya_file_dir)
    if not maya_file_dir.exists():
        raise FileNotFoundError(
            f"Given maya_file_dir doesn't exist on disk: {maya_file_dir}"
        )

    logging_level = logging.DEBUG if parsed.debug else logging.INFO
    configure_logging(maya_file_dir, logging_level)
    logger.debug(parsed)

    search = parsed.search
    search_pattern = fnmatch.translate(search)
    search_pattern = search_pattern.replace("\\Z", "").replace("?s:", "")
    # just to trigger error early
    pattern = re.compile(search_pattern)

    replace = parsed.replace

    if not replace:
        raise ValueError("Missing replace argument.")

    if replace == "::use_maya_file_dir":
        replace = maya_file_dir

    replace = Path(replace)

    if not replace.exists():
        raise FileNotFoundError(f"Path from replace argument doesn't exists: {replace}")

    if not c.Env.get(c.Env.maya_batch):
        logger.warning("! missing MAYA_BATCH_PATH env var. Using default value.")
    maya_batch = c.Env.get(
        c.Env.maya_batch,
        r"C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe",
    )

    ignore_backups = parsed.ignore_backups

    batch_directory(
        maya_files_dir=maya_file_dir,
        search=search_pattern,
        replace=replace,
        maya_batch_path=maya_batch,
        ignore_backups=ignore_backups,
    )


if __name__ == "__main__":
    cli()
