"""

"""
import logging
import sys
import traceback

from Qt import QtCore, QtWidgets

logger = logging.getLogger("m2p.exceptions")


# base errors

class M2pBaseError(BaseException):
    pass


class DisplayedError(M2pBaseError):
    """
    Error linked to a dialog that can be displayed to the user.
    """

    def __init__(self, message):

        super(DisplayedError, self).__init__(message)

        self.dialog = ErrorDialog(
            name="Mash2Pointcloud Error",
            message=message
        )

        self.dialog.show()
        logger.error("[{}] {}".format(self.__class__.__name__, message))

        return


class MayaDevError(M2pBaseError):
    """
    Raise when processing objects related to the Maya scene and the error is
    from a potential code mistake.
    """
    pass


class UserError(DisplayedError):
    """
    When the user did something wrong !
    """
    pass


""" ---------------------------------------------------------------------------

Utilities 

"""


class ErrorHandler(object):
    """ Utility class to handle errors.
    Allow you to stack errors to raise them later.

    Attributes:
        exception:
        data(dict): {str: list of str}

    Examples:
        eh = ErrorHandler(RuntimeError)
        eh.add("object01", "not formated properly")
        eh.raise_error()

    """

    def __init__(self, exception_type):
        """
        Args:
            exception_type: exception to raise
        """
        self.exception = exception_type
        self.data = {}

    def add(self, error_source, error):

        error_value = self.data.get(error_source)
        if error_value:
            error_value.append(error)
        else:
            self.data[error_source] = [error]

        return

    def get_display_string(self, indent=4):
        """
        Args:
            indent(int): indent for error display

        Returns:
            str: errors as a formatted string.
        """
        display_str = ""
        for error_source, error_list in self.data.items():
            display_str += "<{}>:\n".format(error_source)
            for error_value in error_list:
                display_str += "{}{}\n".format(indent*" ", error_value)

        return display_str

    def raise_error(self):
        """
        Raise the error specified at init if the data is not empty.
        """
        if self.data:
            raise self.exception(self.get_display_string())
        else:
            return

    def log(self, _logger, process_title=""):
        """
        Args:
            _logger(logger):
            process_title (str): name to put at the beginning of the log
             message to help identify wher ethe log comes from.
        """
        if not self.data:
            return

        _logger.error(
            "[{}] {}".format(process_title, self.get_display_string()))

        return

    @property
    def length(self):
        """
        Returns:
            int: number of errors holded.
        """
        return len(self.data)

    @property
    def is_empty(self):
        """
        Returns:
            bool: True if there is no error holded
        """
        return True if self.length == 0 else False


class ErrorDialog(QtWidgets.QMessageBox):

    stylesheet = """
    QMessageBox {
        background-color: #232323;
        border: 0px solid #3E3E3E;
        padding: 0px;
        color: #F0F0F0;
        selection-background-color: #1464A0;
        selection-color: #F0F0F0;
    }

    QLabel {
        background-color: transparent;
        border: 0px solid #3E3E3E;
        padding: 0px;
        margin: 0px;
        color: #D94957
    }

    QPushButton {
        background-color: #333333;
        color: #F0F0F0;
        border: 1px solid #444444;
        padding: 5px;
    }

    QPushButton:pressed {
        background-color: #30384E;
        border: 1px solid #6C7CAF;
    }
    """

    def __init__(self, name, message):
        """
        Create a Qt dialog with the given name that will display the given
        message. There is only one button to confirm.

        Args:
            name(str): Name of the Dialog window
            message(str):
        """

        super(ErrorDialog, self).__init__()

        if QtWidgets.QApplication.instance() is None:
            logger.debug(
                "[ErrorDialog][__init__]"
                "No QApplication instance available; creating one."
            )
            QtWidgets.QApplication(sys.argv)

        self.message = message

        self.setWindowTitle(name)
        self.setStyleSheet(self.stylesheet)
        self.setIcon(QtWidgets.QMessageBox.Critical)
        self.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)

        self.setText(message)

        self.btn_quit = QtWidgets.QPushButton("  Confirm  ")
        self.addButton(self.btn_quit, QtWidgets.QMessageBox.AcceptRole)
        self.setEscapeButton(self.btn_quit)

    def show(self):
        self.exec_()
        return


""" ---------------------------------------------------------------------------

Source of the bottom code:
    https://timlehr.com/python-exception-hooks-with-qt-message-box/

Allow to be sure that exception will be raised to the user in an interface.
Exceptions must be a subclass of M2pBaseError.
DisplayedError are ignored.

"""


def show_exception_box(log_msg):
    """
    Raise an error dialog to the user with the Error stacktrace.
    User can only confirm.

    If a QApplication instance is not available (non-console application),
    a QApplication instance is created.
    """
    error_dlg = ErrorDialog(
        name="Mash2pointcloud Error",
        message="An unexpected error occured:\n\n{0}".format(log_msg)
    )

    error_dlg.show()

    return


class UncaughtHook(QtCore.QObject):
    _exception_caught = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        super(UncaughtHook, self).__init__(*args, **kwargs)

        # this registers the exception_hook() function as hook with the
        # Python interpreter
        sys.excepthook = self.exception_hook

        # connect signal to execute the message box function always on
        # main thread
        self._exception_caught.connect(show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        """Function handling uncaught exceptions.
        It is triggered each time an uncaught exception occurs.
        """
        # Only catch Lfb error
        if not issubclass(exc_type, M2pBaseError):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Exclude some execeptions
        if issubclass(exc_type, DisplayedError):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        exc_info = (exc_type, exc_value, exc_traceback)
        log_msg = '\n'.join(
            [''.join(traceback.format_tb(exc_traceback)),
             '{0}: {1}'.format(exc_type.__name__, exc_value)
             ]
        )
        logger.critical("Uncaught exception:\n {0} \n".format(log_msg))

        # trigger message box show
        self._exception_caught.emit(log_msg)
        return
