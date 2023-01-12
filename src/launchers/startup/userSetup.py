import logging
import inspect
import os
import runpy
import shutil
from contextlib import contextmanager

import maya
from maya import cmds


logger = logging.getLogger("userSetup")


class Env:
    """
    Environment Variables
    """

    # optionals
    logging_debug = "LXM_MAYA_PYTHON_LOGGING_DEBUG"
    always_override_prefs = "LXM_MAYA_ALWAYS_OVERRIDE_PREFS"
    # mandatory
    env_dir = "LXM_MAYA_ENV_DIR"
    # mandatory checks
    if not os.getenv(env_dir):
        raise EnvironmentError("Missing variable {}".format(env_dir))


def override_logging():
    """
    Override default maya python root logger with better formatting.
    """

    debug_asked = os.getenv(Env.logging_debug)
    level = logging.DEBUG if debug_asked else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(levelname)-7s | %(asctime)s [%(name)s][%(funcName)s] %(message)s",
        force=True,
    )
    logger.debug("finished overriding python root logger.")
    return


@contextmanager
def catch_exceptions():
    try:
        yield
    except Exception as excp:
        logger.exception("{}".format(excp))


@catch_exceptions()
def setup_maya_plugins_loading():
    """
    Configure which plugin need to be loaded on maya startup.

    The logic is actually dirty where we override the default ``pluginPrefs.mel``
    by a pre-define done, whose path is provided via an env var.
    """

    source_plugin_pref_file = os.getenv(Env.env_dir)
    source_plugin_pref_file = os.path.join(source_plugin_pref_file, "pluginPrefs.mel")

    if not os.path.exists(source_plugin_pref_file):
        logger.warning(
            "returning earlier. {} doesn't exists on disk."
            "".format(source_plugin_pref_file)
        )
        return

    maya_version_prefs_dir = cmds.about(query=True, preferences=True)
    maya_version_prefs_dir = os.path.join(maya_version_prefs_dir, "prefs")

    target_plugin_pref_file = os.path.join(maya_version_prefs_dir, "pluginPrefs.mel")

    shutil.copy2(source_plugin_pref_file, target_plugin_pref_file)
    logger.info(
        "copied {} -> {}".format(source_plugin_pref_file, target_plugin_pref_file)
    )

    logger.info("finished.")
    return


def set_maya_need_restart(need_restart):
    # type: (bool) -> None
    """
    Args:
        need_restart: True to inform the user that maya will need a restart.
    """

    if not need_restart:
        return

    def show_dialog():
        cmds.confirmDialog(
            title="Restart Required",
            message=(
                "This is the first time preferences were initalized.\n"
                "Please close and restart Maya."
            ),
            icon="warning",
        )

    maya.utils.executeDeferred(show_dialog)
    logger.info("Maya will need a restart.")
    return


def set_pref_on_launch():
    """
    Configure user preferences on first launch.

    You can choose to always override prefs with the environemet variable
    ``Env.always_override_prefs``.
    """
    logger.debug("started")

    pref_registered_variable = "customPrefRegistered"
    pref_already_registered = cmds.optionVar(exists=pref_registered_variable)

    if not pref_already_registered:
        set_maya_need_restart(True)

    elif pref_already_registered and not os.getenv(Env.always_override_prefs):
        logger.info("pref already registered, returning early.")
        return

    with catch_exceptions():

        sourcedir = os.getenv(Env.env_dir)
        user_prefs_file = os.path.join(sourcedir, "userPrefs.py")
        runpy.run_path(user_prefs_file)
        logger.info("executed {}".format(user_prefs_file))

    cmds.optionVar(intValue=(pref_registered_variable, 1))
    cmds.savePrefs()

    logger.info("finished. prefs saved.")
    return


if __name__ == "__main__":

    override_logging()
    logger.info("currently executing {}".format(inspect.getsourcefile(lambda: 0)))

    set_pref_on_launch()
    setup_maya_plugins_loading()
