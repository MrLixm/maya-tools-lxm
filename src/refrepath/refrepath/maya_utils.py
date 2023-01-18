import logging
import re
import shutil
from pathlib import Path

from maya import cmds

from .utils import increment_path

logger = logging.getLogger(__name__)


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


def save_scene_and_backup(backup_suffix: str, zfill: int) -> Path:
    """
    Save over the current scene, but realize a backup of it as increment before.

    Args:
        backup_suffix: str to include at the end of the name. ex: ".original"
        zfill: number of zero for padding on file name increment

    Returns:
        existing file path to the backup created
    """

    current_scene_path = Path(cmds.file(query=True, sceneName=True))

    backup_path = current_scene_path.with_stem(current_scene_path.stem + backup_suffix)
    backup_path = increment_path(current_path=backup_path, zfill=zfill)

    logger.info("Saving backup <{}> ...".format(backup_path))
    shutil.copy2(str(current_scene_path), str(backup_path))
    cmds.file(save=True)
    return backup_path
