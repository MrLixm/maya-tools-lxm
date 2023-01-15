import logging
import re
from pathlib import Path

from maya import cmds

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


def save_scene_increment(zfill: int = 4):
    """
    Save the current scene on disk with an increment in its filename.

    Increment are expected to be suffixed just before the file extension separated by a dot.
    Ex: ``myScene.0012.ma``.

    Args:
        zfill:  number of zero for padding on file name increment
    """

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
