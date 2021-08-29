"""

Don't use logging in this module (not configured yet when imported)

"""

import os


""" --------------------------------------------------------------------------- 
Path of the local data on the user's machine
"""
USER_STP_ROOT_DIR = os.path.expanduser(
    os.path.join('~', '.PYCO', "Maya", "mash2pointcloud")
)

USER_LOG_DIR = os.path.join(USER_STP_ROOT_DIR, "logs")
USER_LOG_FILE = os.path.join(USER_LOG_DIR, "m2p.<increment>.log")

""" --------------------------------------------------------------------------- 
Behavior setup
"""

LOG_LEVEL = os.environ.get("M2P_LOG_LVL", "INFO")
LOG_DISK_ENABLE = os.environ.get("M2P_LOG_DISK", False)

"""
"""

