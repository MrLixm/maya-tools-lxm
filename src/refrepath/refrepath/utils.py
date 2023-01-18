import enum
import logging
import os
import re
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


def increment_path(current_path: Path, zfill: int = 4) -> Path:
    """
    From the given file path, increment it until it doesn't exist it on disk.

    Increment are expected to be suffixed just before the file extension separated by a dot.
    Ex: ``myScene.0012.ma``.

    If the current_path has no increment yet at all, it will be added.

    Examples::

        >>> increment_path("C:/demo/file.abc")
        Path("C:/demo/file.0001.abc")  #(0001 doesn't exist on disk)
        >>> increment_path("C:/demo/file.abc", 2)
        Path("C:/demo/file.01.abc")  #(01 doesn't exist on disk)
        >>> increment_path("C:/demo/file.01.abc", 2)
        Path("C:/demo/file.02.abc")

    Args:
        current_path: file path that may or may not exist yet.
        zfill: number of zero for padding on file name increment

    Returns:
        non-existing file path
    """

    increment = 1
    existing_increment = re.search(rf"\.\d{{{zfill}}}$", current_path.stem)
    new_scene_path = Path(current_path)

    while new_scene_path.exists() or increment == 1:

        increment_less_path = current_path.stem
        if existing_increment:
            increment_less_path = increment_less_path.replace(
                existing_increment.group(0), ""
            )

        new_scene_name = increment_less_path + "." + f"{increment}".zfill(zfill)
        new_scene_path = current_path.with_stem(new_scene_name)
        increment += 1

    return new_scene_path


class ColoredFormatter(logging.Formatter):
    """
    References:
        -[1] https://stackoverflow.com/a/56944256/3638629
    """

    class Colors(enum.Enum):
        """

        30-37 foreground :
            0 	black
            1 	red
            2 	green
            3 	yellow
            4 	blue
            5 	magenta
            6 	cyan
            7 	white
        ;
        1 = bold/+intensity
        2 = faint or decreased intensity
        """

        reset = "\x1b[0m"
        black = "\x1b[30m"
        black_bold = "\x1b[30;1m"
        black_faint = "\x1b[30;2m"
        red = "\x1b[31m"
        red_bold = "\x1b[31;1m"
        red_faint = "\x1b[31;2m"
        green = "\x1b[32m"
        green_bold = "\x1b[32;1m"
        green_faint = "\x1b[32;2m"
        yellow = "\x1b[33m"
        yellow_bold = "\x1b[33;1m"
        yellow_faint = "\x1b[33;2m"
        blue = "\x1b[34m"
        blue_bold = "\x1b[34;1m"
        blue_faint = "\x1b[34;2m"
        magenta = "\x1b[35m"
        magenta_bold = "\x1b[35;1m"
        magenta_faint = "\x1b[35;2m"
        cyan = "\x1b[36m"
        cyan_bold = "\x1b[36;1m"
        cyan_faint = "\x1b[36;2m"
        white = "\x1b[37m"
        white_bold = "\x1b[37;1m"
        white_faint = "\x1b[37;2m"
        grey = "\x1b[39m"

    COLOR_BY_LEVEL = {
        logging.DEBUG: Colors.grey,
        logging.INFO: Colors.blue,
        logging.WARNING: Colors.yellow,
        logging.ERROR: Colors.red,
        logging.CRITICAL: Colors.red_bold,
    }

    def __init__(self, fmt, *args, **kwargs):
        super().__init__(fmt, *args, **kwargs)

        self._formatter_by_color = {}
        for color in self.Colors:
            self._formatter_by_color[color.name] = logging.Formatter(
                f"{color.value}{fmt}{color.reset.value}", *args, **kwargs
            )
        self._default_formatter = logging.Formatter(f"{fmt}", *args, **kwargs)

    def format(self, record):

        color = self.COLOR_BY_LEVEL.get(record.levelno, None)
        color = color.name
        if hasattr(record, "color"):
            color = record.color
            delattr(record, "color")

        formatter = self._formatter_by_color.get(color, self._default_formatter)

        return formatter.format(record)
