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


class Env:
    """------------------------------------------------------------------------------------
    ENVIRONMENT VARIABLES

    All are optionals.
    """

    maya_batch = f"MAYA_BATCH_PATH"
    """
    Absolute path to the mayabatch.exe file to use for processing.
    """


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
