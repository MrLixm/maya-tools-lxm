import logging
import os
from contextlib import contextmanager

from maya import cmds

logger = logging.getLogger(__name__)


@contextmanager
def marginwrapper(margin_size):
    """
    Add a left and right margin around widgets wrapped in this context.

    Example::

        >>> with marginwrapper(15):
        >>>     cmds.text(label="test")
        >>>     cmds.text(label="test2")

        is similar to

        >>> cmds.separator(width=15, style="none")
        >>> cmds.text(label="test")
        >>> cmds.text(label="test2")
        >>> cmds.separator(width=15, style="none")
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

    Example::

        >>> @catch_exception()
        >>> def try_something():
        >>>     value = 5 + "3"

        Will show a small window with "TypeError: unsupported operand ..." when executed.
    """
    try:
        yield
    except Exception as excp:
        cmds.confirmDialog(title="Error", icon="error", message=str(excp))
    return


class PathInputDemoWindow:

    NAME = "PathInputDemo"

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
            label="<h1>Path Input</h1>",
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
                command=self.start_process,
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
        """
        Open a file dialog for parsing maya files.
        """
        file_filter = "Maya Files (*.ma *.mb)"
        file_path = cmds.fileDialog2(fileFilter=file_filter, dialogStyle=2, fileMode=1)
        if not file_path:
            return
        file_path = file_path[0]

        cmds.textField(self.textfield_maya_file, edit=True, text=file_path)
        logger.debug("set maya file to {}".format(file_path))
        return

    def browse_root_directory(self, *args):
        """
        Open a file dialog for parsing directories.
        """
        dir_path = cmds.fileDialog2(dialogStyle=2, fileMode=2)
        if not dir_path:
            return
        dir_path = dir_path[0]

        cmds.textField(self.textfield_new_root, edit=True, text=dir_path)
        logger.debug("set root dir to {}".format(dir_path))
        return

    @catch_exception()
    def start_process(self, *args):
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

        if not os.path.exists(maya_file_path):
            raise FileNotFoundError(
                f"Maya file path doesn't exists on disk: {maya_file_path}"
            )

        root_substitute = cmds.textField(self.textfield_new_root, query=True, text=True)

        if not root_substitute:
            raise ValueError("No New Root directory path supplied.")

        if not os.path.exists(root_substitute):
            raise FileNotFoundError(
                f"Root directory path doesn't exists on disk: {root_substitute}"
            )

        logger.info(
            "Executing with root_substitute={}, maya_file_path={}"
            "".format(root_substitute, maya_file_path)
        )
        return

    def show(self):
        cmds.showWindow(self.window)
        return


def gui():
    """
    Create and show the interface to the user
    """

    mywindow = PathInputDemoWindow()
    mywindow.show()

    return


if __name__ == "__main__":
    gui()
