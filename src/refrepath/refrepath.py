"""
Utility to repath references in a maya file.

Must be executed from a Maya context, on an empty scene if possible.
"""
import logging
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


def save_scene_increment():
    """
    Save the current scene on disk with an increment in its filename.
    """
    current_scene_path = Path(cmds.file(query=True, sceneName=True))

    increment = 1
    new_scene_path = Path(current_scene_path)
    while new_scene_path.exists():
        new_scene_name = current_scene_path.stem + "." + f"{increment}".zfill(4)
        new_scene_path = current_scene_path.with_stem(new_scene_name)

    cmds.file(rename=new_scene_path)
    logger.info("Saving {} ...".format(new_scene_path))
    cmds.file(save=True)
    return


def repath_reference(node_name, common_denominator: Path, root_substitute: Path):
    """
    Given the reference node name, edit its path to an existing one so it can be loaded.

    Args:
        node_name: existing maya node name
        common_denominator:
            part of the paths common between initial reference's path and the new root_substitute one.
        root_substitute:
            new "prefix" part of the path to use
    """

    current_path = cmds.referenceQuery(node_name, filename=True, withoutCopyNumber=True)
    if not current_path:
        raise ValueError(f"Cannot retrieve reference file path on {node_name}")

    current_path = Path(current_path)
    logger.info(f"{current_path=}")
    new_path = (
        root_substitute / str(current_path).split(str(common_denominator))[-1][1::]
    )
    logger.info(f"{new_path=}")
    if not new_path.exists():
        raise FileNotFoundError(f"New path computed doesn't exists on disk: {new_path}")

    logger.info("Repathing {} ...".format(node_name))
    try:
        cmds.file(new_path, loadReference=node_name)
    except Exception as excp:
        logger.error(f"{excp}")

    return


def get_references() -> list[str]:
    """
    Retrieve all the references nodes from scene.
    """

    def is_ref_valid(ref_name: str):
        return (
            "sharedReferenceNode" not in ref_name
            and "_UNKNOWN_REF_NODE_" not in ref_name
        )

    scene_reference_list = cmds.ls(type="reference", long=True)
    scene_reference_list = list(filter(is_ref_valid, scene_reference_list))
    return scene_reference_list


def open_and_repath_references(
    maya_file_path: Path,
    common_denominator: Path,
    root_substitute: Path,
):
    """
    Open the given maya file and repath all the references inside.

    Args:
        maya_file_path:
        common_denominator:
            part of the paths common between initial reference's path and the new root_substitute one.
        root_substitute:
            new "prefix" part of the path to use
    """

    logger.info(f"Opening <{maya_file_path}> ...")
    try:
        # still trigger warning but doesn't load references
        cmds.file(maya_file_path, open=True, force=True, loadReferenceDepth="none")
    except Exception as excp:
        logger.error(f"{excp}")

    scene_reference_list = get_references()
    if not scene_reference_list:
        logger.info("Returned early: no references in scene.")

    for index, scene_reference in enumerate(scene_reference_list):

        logger.info(
            f"{index+1}/{len(scene_reference_list)} Repathing {scene_reference} ..."
        )
        repath_reference(
            node_name=scene_reference,
            common_denominator=common_denominator,
            root_substitute=root_substitute,
        )

    save_scene_increment()
    logger.info(f"Finished.")
    return
