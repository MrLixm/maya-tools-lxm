"""
Utility to repath references in a maya file.

Must be executed from a Maya context, on an empty scene if possible.
"""
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# HACK for pycharm autocompletion, actual import is performed in gui() function
# noinspection PyUnreachableCode
if False:
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from PySide2 import QtCore

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
        cmds.confirmDialog(title="Error", icon="warning", message=str(excp))
    return


class RefRepathWidget(QtWidgets.QDialog):

    NAME = "RefRepathWidget"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RefRepath")
        self.setObjectName(self.NAME)
        self.cookUI()
        self.bakeUI()

    def cookUI(self):
        # 1. Create
        self.layout = QtWidgets.QVBoxLayout()
        self.layout_options = QtWidgets.QGridLayout()
        self.label_title = QtWidgets.QLabel(
            "<h1>Utility tool to repath references.</h1>"
        )
        self.label_description = QtWidgets.QLabel(
            (
                "The given Maya file will be opened, all references will be repath. "
                "You then decide how to save it."
            )
        )
        self.label_maya_file = QtWidgets.QLabel("Maya File")
        self.label_root_dir = QtWidgets.QLabel("New Root Directory")
        self.lineedit_maya_file = QtWidgets.QLineEdit()
        self.lineedit_root_dir = QtWidgets.QLineEdit()
        self.button_browse_file = QtWidgets.QPushButton("Browse")
        self.button_browse_dir = QtWidgets.QPushButton("Browse")
        self.button_box = QtWidgets.QDialogButtonBox()
        self.button_execute = QtWidgets.QPushButton("Execute")

        # 2. Add
        self.setLayout(self.layout)
        self.layout.addWidget(self.label_title)
        self.layout.addWidget(self.label_description)
        self.layout.addLayout(self.layout_options)
        self.layout.addWidget(self.button_box)
        self.layout_options.addWidget(self.label_maya_file, 0, 0)
        self.layout_options.addWidget(self.lineedit_maya_file, 0, 1)
        self.layout_options.addWidget(self.button_browse_file, 0, 2)
        self.layout_options.addWidget(self.label_root_dir, 1, 0)
        self.layout_options.addWidget(self.lineedit_root_dir, 1, 1)
        self.layout_options.addWidget(self.button_browse_dir, 1, 2)

        # 3. Modify
        self.layout.setContentsMargins(*(25,) * 4)
        self.layout_options.setContentsMargins(*(15,) * 4)
        self.button_box.setStandardButtons(self.button_box.Cancel)
        self.button_box.addButton(self.button_execute, self.button_box.AcceptRole)
        # 4. Connections
        self.button_box.rejected.connect(self.reject)
        self.button_browse_file.clicked.connect(self.browse_maya_file)
        self.button_browse_dir.clicked.connect(self.browse_root_directory)
        self.button_execute.clicked.connect(self.repath_references)
        return

    def bakeUI(self):
        pass

    def browse_maya_file(self):
        file_filter = "Maya Files (*.ma *.mb)"
        file_path = cmds.fileDialog2(fileFilter=file_filter, dialogStyle=2, fileMode=1)
        if not file_path:
            return
        file_path = file_path[0]
        self.lineedit_maya_file.setText(file_path)
        return

    def browse_root_directory(self):
        dir_path = cmds.fileDialog2(dialogStyle=2, fileMode=2)
        if not dir_path:
            return
        dir_path = dir_path[0]
        self.lineedit_root_dir.setText(dir_path)
        return

    @catch_exception()
    def repath_references(self):
        """
        Main function of the interface
        """

        if cmds.file(query=True, sceneName=True):
            raise RuntimeError(
                "Current scene is already saved on disk. Please execute from a blank scene."
            )

        maya_file_path = self.lineedit_maya_file.text()
        if not maya_file_path:
            raise ValueError("No Maya file path supplied.")

        root_substitute = self.lineedit_root_dir.text()
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


def gui():
    """
    Create and show the interface to the user
    """
    global REFREPATH_WINDOW

    try:
        REFREPATH_WINDOW.close()
        REFREPATH_WINDOW.deleteLater()
        logger.info(f"Removed existing REFREPATH_WINDOW={REFREPATH_WINDOW}")
    except:
        REFREPATH_WINDOW = None

    # deferred imports
    import shiboken2
    import maya.OpenMayaUI
    from PySide2 import QtWidgets
    from PySide2 import QtGui
    from PySide2 import QtCore

    main_window: Optional[QtWidgets.QWidget] = None
    main_window_pointer = maya.OpenMayaUI.MQtUtil.mainWindow()
    if main_window_pointer is not None:
        main_window = shiboken2.wrapInstance(
            int(main_window_pointer), QtWidgets.QWidget
        )

    REFREPATH_WINDOW = RefRepathWidget(parent=main_window)
    REFREPATH_WINDOW.show()
    logger.info(f"Created REFREPATH_WINDOW={REFREPATH_WINDOW}.")
    return


if __name__ == "__main__":
    gui()
