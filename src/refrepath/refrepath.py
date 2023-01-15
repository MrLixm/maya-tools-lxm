"""
Utility to repath references in a maya file.

Must be executed from a Maya context, on an empty scene if possible.
"""
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from maya import cmds

logger = logging.getLogger(__name__)


def repath_reference(
    node_name,
    common_denominator: Path,
    root_substitute: Path,
) -> tuple[Path, Path]:
    """
    Given the reference node name, edit its path to an existing one, so it can be loaded.

    Args:
        node_name: existing maya node name
        common_denominator:
            part of the paths common between initial reference's path and the new root_substitute one.
        root_substitute:
            new "prefix" part of the path to use

    Returns:
        previous path, and new path set as tuple[previous_path, new_path].
        Can be the same path value for both.

    Raises:
        ValueError: cannot retrieve reference file path
        FileNotFoundError: new path computed doesn't exist on disk
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
        raise FileNotFoundError(f"New path computed doesn't exist on disk: {new_path}")

    if current_path == new_path:
        logger.info(f"Returning earlier, path is already good on <{node_name}>")
        return current_path, new_path

    logger.info(f"new_path{new_path}")

    logger.info(f"Repathing <{node_name}> ...")
    # a reference repath can fail because of unkown node, we usually want to ignore that
    # so that's why we just log the error and still consider the repathing sucessful.
    try:
        cmds.file(str(new_path), loadReference=node_name)
    except Exception as excp:
        logger.error(f"{excp}")

    return current_path, new_path


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


ReferenceRepathingResultType = dict[str, dict[str, Path]]


def open_and_repath_references(
    maya_file_path: Path,
    common_denominator: Path,
    root_substitute: Path,
) -> ReferenceRepathingResultType:
    """
    Open the given maya file and repath all the references inside.

    Args:
        maya_file_path:
        common_denominator:
            part of the paths common between initial reference's path and the new root_substitute one.
        root_substitute:
            new "prefix" part of the path to use

    Returns:
        dict of references repathed with their path values as
        dict["ref name": {"previous": "file path", "new": "file path"}]
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

    repathed_references = {}

    for index, scene_reference in enumerate(scene_reference_list):

        logger.info(
            f"{index+1}/{len(scene_reference_list)} Repathing {scene_reference} ..."
        )
        previous_path, new_path = repath_reference(
            node_name=scene_reference,
            common_denominator=common_denominator,
            root_substitute=root_substitute,
        )
        repathed_references[scene_reference] = {
            "previous": previous_path,
            "new": new_path,
        }

    logger.info(f"Finished.")
    return repathed_references


"""-------------------------------------------------------------------------------------

GUI

"""


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


def gui():
    """
    Create and show the interface to the user
    """
    # deferred imports
    import shiboken2
    import maya.OpenMayaUI
    from PySide2 import QtWidgets
    from PySide2 import QtCore

    class RefRepathResultDialog(QtWidgets.QDialog):

        NAME = "RefRepathResultDialog"

        def __init__(self, repathing_result: ReferenceRepathingResultType, parent=None):
            super().__init__(parent)
            self._repathing_result: ReferenceRepathingResultType = repathing_result
            self.setWindowTitle("RefRepath Result Dialog")
            self.setObjectName(self.NAME)
            self.cookUI()
            self.bakeUI()

        def cookUI(self):
            # 1. Create
            self.layout = QtWidgets.QVBoxLayout()
            self.label_title = QtWidgets.QLabel("<h1>Repathing Finished</h1>")
            self.label_description = QtWidgets.QLabel()
            self.treewidget = QtWidgets.QTreeWidget()
            self.button_box = QtWidgets.QDialogButtonBox()

            # 2. Add
            self.setLayout(self.layout)
            self.layout.addWidget(self.label_title)
            self.layout.addWidget(self.label_description)
            self.layout.addWidget(self.treewidget)
            self.layout.addWidget(self.button_box)

            # 3. Modify
            self.layout.setSpacing(15)
            self.layout.setContentsMargins(*(25,) * 4)
            self.label_title.setAlignment(QtCore.Qt.AlignCenter)
            self.button_box.setStandardButtons(self.button_box.Ok)
            self.treewidget.setColumnCount(2)
            self.treewidget.setMinimumHeight(150)
            self.treewidget.setAlternatingRowColors(True)
            self.treewidget.setSortingEnabled(True)
            self.treewidget.setUniformRowHeights(True)
            self.treewidget.setRootIsDecorated(True)
            self.treewidget.setItemsExpandable(True)
            # select only one row at a time
            self.treewidget.setSelectionMode(self.treewidget.SingleSelection)
            # select only rows
            self.treewidget.setSelectionBehavior(self.treewidget.SelectRows)
            # remove dotted border on columns
            self.treewidget.setFocusPolicy(QtCore.Qt.NoFocus)
            self.treewidget.setHeaderLabels(["Reference", "Paths"])
            # 4. Connections
            self.button_box.accepted.connect(self.accept)
            self.button_box.rejected.connect(self.reject)
            return

        def bakeUI(self):
            self.label_description.setText(
                f"Repathed {len(self._repathing_result)} references."
            )

            self.treewidget.clear()

            for ref_name, ref_result in self._repathing_result.items():
                item_ref = QtWidgets.QTreeWidgetItem(self.treewidget)
                item_ref.setText(0, ref_name)

                item_previous = QtWidgets.QTreeWidgetItem(item_ref)
                item_previous.setText(0, "previous")
                item_previous.setText(1, str(ref_result["previous"]))
                item_new = QtWidgets.QTreeWidgetItem(item_ref)
                item_new.setText(0, "new")
                item_new.setText(1, str(ref_result["new"]))

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
            self.layout.setSpacing(15)
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
            file_path = cmds.fileDialog2(
                fileFilter=file_filter, dialogStyle=2, fileMode=1
            )
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
            repathed_references = open_and_repath_references(
                maya_file_path=maya_file_path,
                common_denominator=common_denominator,
                root_substitute=root_substitute,
            )

            result_dialog = RefRepathResultDialog(
                repathing_result=repathed_references,
                parent=self,
            )
            result_dialog.show()
            logger.info("Finished")
            return

    global REFREPATH_WINDOW

    try:
        REFREPATH_WINDOW.close()
        REFREPATH_WINDOW.deleteLater()
        logger.info(f"Removed existing REFREPATH_WINDOW={REFREPATH_WINDOW}")
    except:
        REFREPATH_WINDOW = None

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
