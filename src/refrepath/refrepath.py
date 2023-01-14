"""
Utility to repath references in a maya file.

Must be executed from a Maya context, on an empty scene if possible.
"""
import logging
from contextlib import contextmanager
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
    logger.info(f"current_path={current_path}")

    new_path = (
        root_substitute / str(current_path).split(str(common_denominator))[-1][1::]
    )

    if not new_path.exists():
        raise FileNotFoundError(f"New path computed doesn't exists on disk: {new_path}")

    if current_path == new_path:
        logger.info(f"Returning earlier, path is already good on <{node_name}>")
        return

    logger.info(f"new_path{new_path}")

    logger.info(f"Repathing <{node_name}> ...")
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
    save_scene: bool = True,
):
    """
    Open the given maya file and repath all the references inside.

    Args:
        maya_file_path:
        common_denominator:
            part of the paths common between initial reference's path and the new root_substitute one.
        root_substitute:
            new "prefix" part of the path to use
        save_scene:
            True to save and increment the scen eonce finished
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

    if save_scene:
        save_scene_increment()
    logger.info(f"Finished.")
    return


"""-------------------------------------------------------------------------------------

GUI

"""


@contextmanager
def marginwrapper(margin_size):
    """
    Add a left and right margin around everything wrapped in this context.
    """
    cmds.separator(width=margin_size, style="none")
    try:
        yield
    finally:
        cmds.separator(width=margin_size, style="none")
    return


@contextmanager
def catch_exception():
    """
    Catch all exception in a dialog raised to user.
    """
    try:
        yield
    except Exception as excp:
        cmds.confirmDialog(title="Error", icon="error", message=str(excp))
    return


class RefRepathWindow:

    NAME = "RefRepath"

    def __init__(self):

        self.delete_if_exists()
        self.window = cmds.window(self.NAME, title=self.NAME, widthHeight=(800, 200))
        self.build()

    def build(self):
        """
        We build all the interface elements in this method.
        """

        class Style:
            padding_main_window = 15
            width_button = 80
            margin_widget_base = 10

        self.layout_main = cmds.rowColumnLayout(adjustableColumn=1)
        cmds.separator(height=10, style="none")
        cmds.text(
            label="<h1>Utility to repath references.</h1>",
            align="center",
            recomputeSize=True,
        )
        cmds.separator(height=20, style="none")
        cmds.text(
            label=(
                "The given Maya file will be opened, all references will be repath."
                "You the decide how to save it."
            ),
            align="center",
            recomputeSize=True,
        )
        cmds.separator(height=20, style="none")
        self.layout_options = cmds.rowColumnLayout(numberOfColumns=5)
        cmds.rowColumnLayout(self.layout_options, edit=True, adjustableColumn=3)
        cmds.rowColumnLayout(self.layout_options, edit=True, columnAlign=[2, "center"])
        cmds.rowColumnLayout(
            self.layout_options,
            edit=True,
            rowSpacing=[1, Style.margin_widget_base],
        ),
        cmds.rowColumnLayout(
            self.layout_options,
            edit=True,
            columnSpacing=[3, Style.margin_widget_base],
        )
        cmds.rowColumnLayout(
            self.layout_options,
            edit=True,
            columnSpacing=[4, Style.margin_widget_base],
        )

        first_column_size = 130

        with marginwrapper(Style.padding_main_window):

            cmds.text(
                label="Maya File",
                align="right",
                font="boldLabelFont",
                recomputeSize=False,
                width=first_column_size,
            )
            self.textfield_maya_file = cmds.textField(
                annotation="Path to a Maya file.",
            )
            self.button_browse_file = cmds.button(
                label="Browse",
                command=self.browse_maya_file,
                width=Style.width_button,
            )

        with marginwrapper(Style.padding_main_window):

            cmds.text(
                label="New Root Directory",
                align="right",
                font="boldLabelFont",
                width=first_column_size,
            )
            self.textfield_new_root = cmds.textField(
                annotation="Path to an existing directory.",
            )
            self.button_browse_root = cmds.button(
                label="Browse",
                command=self.browse_root_directory,
                width=Style.width_button,
            )
        # end the layout_options
        cmds.setParent("..")

        cmds.separator(height=10, style="none")

        self.layout_button01 = cmds.rowColumnLayout(numberOfColumns=5)
        cmds.rowColumnLayout(self.layout_button01, edit=True, adjustableColumn=1)
        cmds.rowColumnLayout(
            self.layout_button01,
            edit=True,
            columnSpacing=[4, Style.margin_widget_base],
        )

        cmds.separator(width=1, style="none")  # adjustable column

        with marginwrapper(Style.padding_main_window):

            self.button_start = cmds.button(
                label="Start",
                command=self.repath_references,
                width=Style.width_button,
            )
            self.button_cancel = cmds.button(
                label="Cancel",
                command=self.delete_if_exists,
                width=Style.width_button,
            )
        # end the layout_button01
        cmds.setParent("..")

        # end the layout_main
        cmds.setParent("..")
        return

    def delete_if_exists(self, *args):
        if cmds.windowPref(self.NAME, query=True, exists=True):
            cmds.windowPref(self.NAME, remove=True)
        if cmds.window(self.NAME, query=True, exists=True):
            cmds.deleteUI(self.NAME, window=True)
        return

    def browse_maya_file(self, *args):
        file_filter = "Maya Files (*.ma *.mb)"
        file_path = cmds.fileDialog2(fileFilter=file_filter, dialogStyle=2, fileMode=1)
        if not file_path:
            return
        file_path = file_path[0]
        cmds.textField(self.textfield_maya_file, edit=True, text=file_path)
        return

    def browse_root_directory(self, *args):
        dir_path = cmds.fileDialog2(dialogStyle=2, fileMode=2)
        if not dir_path:
            return
        dir_path = dir_path[0]
        cmds.textField(self.textfield_new_root, edit=True, text=dir_path)
        return

    @catch_exception()
    def repath_references(self, *args):
        """
        Main function of the interface
        """

        if cmds.file(query=True, sceneName=True):
            raise RuntimeError(
                "Current scene is already saved on disk. Please execute from a blank scene."
            )

        maya_file_path = cmds.textField(self.textfield_maya_file, query=True, text=True)
        if not maya_file_path:
            raise ValueError("No Maya file path supplied.")

        root_substitute = cmds.textField(self.textfield_new_root, query=True, text=True)
        if not root_substitute:
            raise ValueError("No New Root directory path supplied.")

        maya_file_path = Path(maya_file_path)
        if not maya_file_path.exists():
            raise FileNotFoundError(
                f"Maya file path doesn't exists on disk: {maya_file_path}"
            )

        root_substitute = Path(root_substitute)
        if not root_substitute.exists():
            raise FileNotFoundError(
                f"Root directory path doesn't exists on disk: {root_substitute}"
            )

        common_denominator = Path(root_substitute.name)
        open_and_repath_references(
            maya_file_path=maya_file_path,
            common_denominator=common_denominator,
            root_substitute=root_substitute,
            save_scene=False,
        )
        return

    def show(self):
        cmds.showWindow(self.window)
        return


def gui():
    """
    Create and show the interface to the user
    """

    mywindow = RefRepathWindow()
    mywindow.show()

    return


if __name__ == "__main__":
    gui()
