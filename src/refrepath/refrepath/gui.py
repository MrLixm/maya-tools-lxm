import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import shiboken2
import maya.OpenMayaUI
from PySide2 import QtWidgets
from PySide2 import QtCore
from maya import cmds

import refrepath
from refrepath.core import RepathedReference
from refrepath.core import open_and_repath_references

logger = logging.getLogger(__name__)


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


class RefRepathResultDialog(QtWidgets.QDialog):

    NAME = "RefRepathResultDialog"

    def __init__(self, repathing_result: list[RepathedReference], parent=None):
        super().__init__(parent)
        self._repathing_result: list[RepathedReference] = repathing_result
        self.setWindowTitle("RefRepath Result Dialog")
        self.setObjectName(self.NAME)
        self.cookUI()
        self.bakeUI()

    def cookUI(self):
        # 1. Create
        self.layout = QtWidgets.QVBoxLayout()
        self.label_title = QtWidgets.QLabel("<h1>Repathing Finished</h1>")
        self.label_description = QtWidgets.QLabel()
        self.label_info = QtWidgets.QLabel(
            "All references are currently unloaded and need to be reloaded if you "
            "want to work on the scene.\n"
            "You can also just save and close the scene, references will be "
            "loaded the next time you open it."
        )
        self.treewidget = QtWidgets.QTreeWidget()
        self.button_box = QtWidgets.QDialogButtonBox()

        # 2. Add
        self.setLayout(self.layout)
        self.layout.addWidget(self.label_title)
        self.layout.addWidget(self.label_description)
        self.layout.addWidget(self.label_info)
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

        for repathed_reference in self._repathing_result:
            item_ref = QtWidgets.QTreeWidgetItem(self.treewidget)
            item_ref.setText(0, repathed_reference.node_name)

            item_previous = QtWidgets.QTreeWidgetItem(item_ref)
            item_previous.setText(0, "previous")
            item_previous.setText(1, str(repathed_reference.previous_path))
            item_new = QtWidgets.QTreeWidgetItem(item_ref)
            item_new.setText(0, "new")
            item_new.setText(1, str(repathed_reference.new_path))

        return


class RefRepathWidget(QtWidgets.QDialog):

    NAME = "RefRepathWidget"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RefRepath")
        self.setObjectName(self.NAME)
        self.cookUI()

    def cookUI(self):
        # 1. Create
        self.layout = QtWidgets.QVBoxLayout()
        self.layout_options = QtWidgets.QGridLayout()
        self.label_title = QtWidgets.QLabel(
            f"<h1>RefRepath v{refrepath.__version__}</h1>"
            f"<h4>Utility tool to repath references.</h4>"
        )
        self.label_description = QtWidgets.QLabel(
            (
                "The given Maya file will be opened, all references will be repath. "
                "You then decide how to save it."
            )
        )
        self.label_maya_file = QtWidgets.QLabel("Maya File")
        self.label_root_dir = QtWidgets.QLabel("New Root Directory")
        self.label_denominator = QtWidgets.QLabel("Common Denominator")
        self.lineedit_maya_file = QtWidgets.QLineEdit()
        self.lineedit_root_dir = QtWidgets.QLineEdit()
        self.lineedit_denominator = QtWidgets.QLineEdit()
        self.button_browse_file = QtWidgets.QPushButton("Browse")
        self.button_browse_dir = QtWidgets.QPushButton("Browse")
        self.checkbox_denominator = QtWidgets.QCheckBox("Edit")
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
        self.layout_options.addWidget(self.label_denominator, 2, 0)
        self.layout_options.addWidget(self.lineedit_denominator, 2, 1)
        self.layout_options.addWidget(self.checkbox_denominator, 2, 2)

        # 3. Modify
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(*(25,) * 4)
        self.layout_options.setContentsMargins(*(15,) * 4)
        self.button_box.setStandardButtons(self.button_box.Cancel)
        self.button_box.addButton(self.button_execute, self.button_box.AcceptRole)
        self.checkbox_denominator.setChecked(False)
        # 4. Connections
        self.button_box.rejected.connect(self.reject)
        self.button_browse_file.clicked.connect(self.browse_maya_file)
        self.button_browse_dir.clicked.connect(self.browse_root_directory)
        self.button_execute.clicked.connect(self.repath_references)
        self.checkbox_denominator.stateChanged.connect(
            self.on_checkbox_denominator_change
        )
        self.lineedit_root_dir.textChanged.connect(self.on_checkbox_denominator_change)
        return

    def on_checkbox_denominator_change(self, *args):
        checked = self.checkbox_denominator.isChecked()
        self.lineedit_denominator.setEnabled(checked)
        self.label_denominator.setEnabled(checked)

        root_dir = self.lineedit_root_dir.text()

        if not checked and root_dir:
            root_dir = Path(root_dir)
            self.lineedit_denominator.setText(root_dir.name)

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

        common_denominator = self.lineedit_denominator.text()
        if not common_denominator:
            raise ValueError("No Common Denominator directory path supplied.")

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

        if common_denominator not in str(root_substitute):
            raise ValueError(
                f"Denominator has to be found in the New Root Directory: "
                f"<{common_denominator}> not in <{root_substitute}>"
            )
        common_denominator = Path(common_denominator)

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


def gui():
    """
    Create and show the interface to the user
    """
    # deferred imports

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
