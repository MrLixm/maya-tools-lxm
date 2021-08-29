"""

"""
import glob
import logging
import os
import re
import time

import maya.cmds as cmds

logger = logging.getLogger("m2p.core.alembicExporter")


def export_abc(export_settings):
    """
    Method to export the Abc

    Args:
        export_settings(AbcExportSettings):
    """
    s_time = time.clock()

    dir_path = os.path.dirname(export_settings.target_filepath)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    export_command = [
        "-frameRange",
        export_settings.frame_start,
        export_settings.frame_stop,
        "-uvWrite",
        "-writeFaceSets",
        "-worldSpace",
        "-writeVisibility",
        "-noNormals",
        "-stripNamespaces",
        "-autoSubd",
        "-dataFormat",
        "ogawa",
        "-root",
        export_settings.dag_objects,
        "-file",
        export_settings.target_filepath,
    ]
    export_command = " ".join(export_command)

    cmds.AbcExport(j=export_command)

    if not os.path.exists(export_settings.target_filepath):
        raise RuntimeError("The abc was not exported")

    logger.info(
        "[export_abc] Finished in {}s for {}"
        "".format(time.clock() - s_time,
                  os.path.basename(export_settings.target_filepath))
    )
    return


class AbcExportSettings(object):

    increment_decimal_number = 4

    def __init__(self):
        self.dag_objects = None
        self.frame_start = 1
        self.frame_stop = 1
        self.target_dir = None  # type: str
        self.target_basename = None  # type: str
        self.version = None  # type: str

    @property
    def target_filepath(self):
        """ Build the final path with the root directory + the final directory
        + target_basename + version + .abc

        Returns:
            str: somepath\filename.abc
        """

        if not self.target_dir:
            raise ValueError("[AbcExportSettings][target_filepath]"
                             "self.target_dir is empty.")

        if not self.target_basename:
            raise ValueError("[AbcExportSettings][target_filepath]"
                             "self.target_basename is empty.")

        if self.target_basename.endswith(".abc"):
            raise ValueError("[AbcExportSettings][target_filepath]"
                             "self.target_basename end with <.abc>, this was "
                             "not excepted.")

        if not self.version:
            self.find_version()

        final_basename = "{}.{}.abc".format(self.target_basename, self.version)
        final_path = os.path.join(
            self.target_dir,
            final_basename
        )
        logger.debug("[AbcExportSettings][target_filepath] Final path returned"
                     "is <{}>".format(final_path))
        return final_path

    def find_version(self):
        """ Set and return self.version incremented.

        Returns:
            str: incremented version, ex: "0001"
        """

        if not os.path.exists(self.target_dir):
            self.version = "1".zfill(self.increment_decimal_number)
            logger.debug(
                "[AbcExportSettings][find_version] No version found, set to"
                "<{}>.".format(self.version))
            return self.version

        existing_files = glob.glob(
            os.path.join(self.target_dir, "{}.*.abc".format(self.target_basename))
        )
        if not existing_files:
            self.version = "1".zfill(self.increment_decimal_number)
            logger.debug(
                "[AbcExportSettings][find_version] No version found, set to"
                "<{}>.".format(self.version))
            return self.version

        existing_files = sorted(existing_files)
        last_increment = os.path.basename(existing_files[-1])
        last_increment = os.path.splitext(last_increment)[0]
        last_increment = int(last_increment.split(".")[-1])
        new_increment = str(last_increment + 1)
        new_increment = new_increment.zfill(self.increment_decimal_number)

        logger.debug("[AbcExportSettings][find_version] Last version was <{}>"
                     ", incremented to <{}>."
                     "".format(last_increment, new_increment))
        self.version = new_increment
        return self.version
