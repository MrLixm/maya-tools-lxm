"""
Constants.
Lowest level module.
"""
from __future__ import annotations

__all__ = ("name", "__version__")

import enum
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

__version_major__ = 0
__version_minor__ = 1
__version_patch__ = 0
__version__ = f"{__version_major__}.{__version_minor__}.{__version_patch__}"

name = "refrepath"
"""
Package name. Must be special-characters free
"""

vcs_url = "https://github.com/MrLixm/Autodesk_Maya/tree/main/src/refrepath"
"""
url of the remote VCS repository for this package.
"""


""" ------------------------------------------------------------------------------------
ENVIRONMENT VARIABLES

All are optionals.
"""

ENVPREFIX = name.upper()


class Env(enum.Enum):

    # TODO see if needed to keep
    logs_debug = f"{ENVPREFIX}_LOGS_DEBUG"
    """
    Set logging to debug level
    """

    debug = f"{ENVPREFIX}_DEBUG"
    """
    Enable the debug mode for the application
    """

    maya_batch = f"MAYA_BATCH_PATH"
    """
    Absolute path to the mayabatch.exe file to use for processing.
    """

    @classmethod
    def __all__(cls):
        return [attr for attr in cls]

    @classmethod
    def __asdict__(cls) -> dict[str, str]:
        out = dict()
        for attr in cls.__all__():
            out[str(attr.value)] = cls.get(attr)
        return out

    @classmethod
    def get(cls, key: Env, default: Any = None) -> str | None | Any:
        return os.environ.get(str(key.value), default)


""" ------------------------------------------------------------------------------------
CONFIGURATION

Can be changed during runtime
"""

DRYRUN = False
"""
True to process the code by making sure nothing is wrote/edited from disk.
True is often used for debugging purposes.
"""

PATH_ZFILL: int = 4
"""
Number of zero to use on file path increment.
"""

PATH_BACKUP_SUFFIX: str = ".refrepathbackup"
"""
string to use as suffix on file path for backups
"""
