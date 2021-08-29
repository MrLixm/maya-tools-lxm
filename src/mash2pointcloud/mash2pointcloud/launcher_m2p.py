
import logging
import logging.config
import os
import sys

from . import config_m2p as config
from . import constants_m2p as constants

logger = logging.getLogger("m2p.launcher")


def _get_log_file_path():
    """

    Returns:
        str: Path of the existing logging file for the package
    """
    log_path = config.USER_LOG_FILE.replace(
        "<increment>",
        "main")

    if os.path.exists(log_path):
        return log_path

    # first time creation for the log so create the dir and the file.
    log_dirpath = os.path.dirname(log_path)
    if not os.path.exists(log_dirpath):
        os.makedirs(log_dirpath)

    # create the file by opening it
    with open(log_path, 'w'):
        pass

    return log_path


def _configure_logging():
    """
    Configure the python logging module
    """

    # create the .log file if the config specified it.
    if config.LOG_DISK_ENABLE:
        user_log_path = _get_log_file_path()
        handler_disk_class = "logging.handlers.RotatingFileHandler"
    else:
        user_log_path = ""
        handler_disk_class = "logging.handlers.NullHandler"

    logging_config = {

        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "fmt_standard": {
                "format": "[spb][%(levelname)7s] %(asctime)s [%(name)38s] //%(message)s"
            }
        },

        "handlers": {
            "hl_console": {
                "level": "DEBUG",
                "formatter": "fmt_standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout"
            },
            "hl_disk": {
                "level": "INFO",
                "formatter": "fmt_standard",
                "class": handler_disk_class,
                "filename": user_log_path,
                "mode": "a",
                "maxBytes": 150000,
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },

        "loggers": {
            "amgr": {
                "handlers": [
                    "hl_console",
                    "hl_disk"
                ],
                "level": config.LOG_LEVEL,
                "propagate": False
            },
            "amgr.debug": {
                "handlers": [
                    "hl_console",
                    "hl_disk"
                ],
                "level": config.LOG_LEVEL,
                "propagate": False
            },
            "amgr.core.__init__": {
                "handlers": [
                    "hl_console"
                ],
                "level": config.LOG_LEVEL,
                "propagate": False
            },
            "amgr.gui": {
                "handlers": [
                    "hl_console",
                    "hl_disk"
                ],
                "level": config.LOG_LEVEL,
                "propagate": False
            },
        }
    }
    # register
    logging.config.dictConfig(logging_config)

    return


""" ---------------------------------------------------------------------------
PUBLIC
"""


def initial_logging():
    """ Start the logging system

    Returns:
        None
    """

    _configure_logging()
    logger.info("[initial_logging] Completed.")

    return


def register_vendor():
    """ Add the vendor directory to the path.

    Returns:
        None
    """

    if constants.VENDOR_DIR not in sys.path:
        sys.path.append(constants.VENDOR_DIR)
        logger.debug("[register_vendor] Vendor dir added to sys.path")

    return

