"""
version=1
author="Liam Collod<monsieurlixm@gmail.com>"
dependencies=[
    "python>3.8",
    "maya~=2023",
    "refrepath.py",
]
description="Repath references in multiple maya files at once."
instructions=\"\"\"

    Must be executed from the command line with an available python interpreter:

        python -m refrepath_project.py --help

    Environment variables:
        - MAYA_BATCH_PATH : path to the mayabatch.exe file on your system

\"\"\"
"""
import argparse
import datetime
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)

MAYA_BATCH = os.getenv("MAYA_BATCH_PATH")
if not MAYA_BATCH:
    logger.warning("! missing MAYA_BATCH_PATH env var. Using default value.")
    MAYA_BATCH = r"C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe"
MAYA_BATCH = Path(MAYA_BATCH)

REFREPATH_PACKAGE = Path(__file__).parent

DRYRUN = False


def configure_logging(root_path: Path, level: int):
    """
    Configure the python logging system for the processing of the given directory.

    Args:
        root_path: path to an existing directory
        level: logging level to set the console logger to
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "{levelname: <7} | {asctime} [{name}][{funcName}] {message}", style="{"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if DRYRUN:
        return

    disk_handler_filename = (
        f"refrepath-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    )
    disk_handler = logging.FileHandler(root_path / disk_handler_filename)
    disk_handler.setLevel(logging.DEBUG)
    disk_handler.setFormatter(formatter)
    logger.addHandler(disk_handler)
    return


def override_maya_logging():
    """
    Override default maya python logger with a better formatter
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format="{levelname: <7} | {asctime} [{name}][{funcName}] {message}",
        style="{",
        force=True,
    )
    return


def save_scene_increment():
    """
    Save the current scene on disk with an increment in its filename.

    To execute from a maya context.
    """
    from maya import cmds

    # number of zero for padding
    zfill = 4

    current_scene_path = Path(cmds.file(query=True, sceneName=True))

    increment = 1
    existing_increment = re.search(rf"\.\d{{{zfill}}}$", current_scene_path.stem)
    new_scene_path = Path(current_scene_path)

    while new_scene_path.exists() or increment == 1:

        increment_less_path = current_scene_path.stem
        if existing_increment:
            increment_less_path = increment_less_path.replace(
                existing_increment.group(0), ""
            )

        new_scene_name = increment_less_path + "." + f"{increment}".zfill(zfill)
        new_scene_path = current_scene_path.with_stem(new_scene_name)
        increment += 1

    cmds.file(rename=new_scene_path)
    logger.info("Saving {} ...".format(new_scene_path))
    cmds.file(save=True)
    return


def get_child_files_from_root(
    root_path: Path,
    recursive: bool = True,
    extensions_filter: Optional[list[str]] = None,
) -> list[Path]:
    """
    Return all the files and sub-files in the given directory.

    Args:
        root_path: existing directory path to start the parsing from
        extensions_filter: list of file extensions to keep. Other extensions are ignored.
            default is <.py>
        recursive: True to also process each directory encountered
    """
    out = list()

    for entry in os.scandir(root_path):

        entry = Path(entry.path)

        if entry.is_dir() and recursive:
            out.extend(
                get_child_files_from_root(
                    entry,
                    recursive=True,
                    extensions_filter=extensions_filter,
                )
            )

        else:

            if extensions_filter and entry.suffix in extensions_filter:
                out.append(entry)
            elif not extensions_filter:
                out.append(entry)

    return out


def get_maya_file_to_process(root_path) -> list[Path]:
    """
    Parse the given directopry and all its subdirectories for maya files.
    """
    logger.info(f"Started with root_path={root_path}")

    maya_file_list = get_child_files_from_root(
        root_path=root_path,
        recursive=True,
        extensions_filter=[".mb", ".ma"],
    )

    return maya_file_list


def get_log_file(maya_file: Path) -> Path:
    """
    Get the path of the log file to use for the give maya-file.

    The log file is used to write logs for the repath operation.

    Args:
        maya_file: path to an existing maya file

    Returns:
        valid path to a non-existing yet file
    """
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = maya_file.parent / f"refrepath-{maya_file.name}-{current_time}.log"
    return log_path


def process_file(
    maya_file: Path,
    common_denominator: Path,
    root_substitute: Path,
    logs_path: Path,
):
    """
    Create a subprocess to process and open the given maya file.
    """

    log_prefix = maya_file.name

    maya_python_command = (
        "import maya.mel;"
        "import refrepath;"
        "import refrepath_batch;"
        "from pathlib import Path;"
        "maya.mel.eval('stackTrace -state on');"
        "refrepath_batch.override_maya_logging();"
        "refrepath.open_and_repath_references("
        f"    maya_file_path=Path(r'{maya_file}'),"
        f"    common_denominator=Path(r'{common_denominator}'),"
        f"    root_substitute=Path(r'{root_substitute}'),"
        ");"
        "refrepath_batch.save_scene_increment();"
    )
    maya_python_command = repr(maya_python_command).lstrip('"').rstrip('"')

    process_command = [
        str(MAYA_BATCH),
        "-command",
        f'"python(\\"{maya_python_command}\\")"',
        "-log",
        str(logs_path),
    ]
    process_command = " ".join(process_command)

    process_env = dict(os.environ)
    python_path = process_env.get("PYTHON_PATH", "")
    python_path += f"{os.pathsep}{str(REFREPATH_PACKAGE)}"
    process_env["PYTHONPATH"] = python_path
    # network crap optimizations
    process_env["MAYA_DISABLE_CLIC_IPM"] = "1"
    process_env["MAYA_DISABLE_CIP"] = "1"
    process_env["MAYA_DISABLE_CER"] = "1"
    process_env["MAYA_DISABLE_ADP"] = "1"
    # when script executed from pycharm or else, just by safety.
    if "VIRTUAL_ENV" in process_env:
        del process_env["VIRTUAL_ENV"]

    logger.debug(f"<{log_prefix}> process_command={process_command}")
    logger.info(f"<{log_prefix}> About to be processed  ...")

    if DRYRUN:
        logger.info("Returned earlier. DRYRUN=True")
        return

    time_start = time.time()

    try:
        process_result = subprocess.run(
            process_command,
            capture_output=True,
            check=True,
            env=process_env,
        )
    except subprocess.CalledProcessError as excp:
        process_result = None
        logger.error(f"<{log_prefix}>:{maya_file}:{excp}")

    logger.debug(f"<{log_prefix}> Result:\n{process_result}")
    logger.info(f"<{log_prefix}> Finished in {time.time() - time_start}s")
    return


def process_all_maya_files_from(parse_root_path: Path, root_substitute_path: Path):
    """
    Parse the given directory to find all maya file and repath all references inside them.

    Args:
        parse_root_path: initial directory to parse recursively for maya files.
        root_substitute_path: directory path used as root for reference repathing.
    """

    logger.info(
        f"Started with parse_root_path={parse_root_path}, "
        f"root_substitute_path={root_substitute_path}"
    )

    common_denominator = Path(root_substitute_path.name)

    maya_file_list = get_maya_file_to_process(parse_root_path)
    logger.info(f"About to process {len(maya_file_list)} files.")

    for file_index, maya_file in enumerate(maya_file_list):

        log_path = get_log_file(maya_file)
        process_file(
            maya_file,
            common_denominator=common_denominator,
            root_substitute=root_substitute_path,
            logs_path=log_path,
        )

        logger.info(f"{file_index+1}/{len(maya_file_list)} completed.")
        continue

    logger.info("Finished.")
    return


def cli():
    """
    Command line argument for processing arg submitted by user.
    """
    global DRYRUN

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
        DRYRUN = True

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
    process_all_maya_files_from(parse_root_path, substitute_root_path)


if __name__ == "__main__":
    cli()
