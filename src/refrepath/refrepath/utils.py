import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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


def get_maya_files_recursively(root_path) -> list[Path]:
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
