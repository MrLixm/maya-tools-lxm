"""

"""
from . import launcher_m2p

launcher_m2p.initial_logging()
launcher_m2p.register_vendor()

""" 02. -----------------------------------------------------------------------
Start exception handler
Allow us to be sure that unhandled exception will be raised to the user 
in an interface and caught in the logger.

# create a global instance of the class to register the hook
"""

from . import exceptions_m2p

qt_exception_hook = exceptions_m2p.UncaughtHook()

""" 03. -----------------------------------------------------------------------
Finish the package imports
"""

from . import constants_m2p as constants
from .constants_m2p import (
    VERSION,
    APPNAME,
    APPNAME_UI
)

from . import core
from . import gui
