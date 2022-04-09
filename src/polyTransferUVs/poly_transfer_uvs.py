"""
version=1.0.3
author=Liam Collod
last_modified=09/04/2022
contact=monsieurlixm@gmail.com
python>2.7
maya=?

[What]

Transfer UVs from one object to multiple objects.
Change the SAMPLE_SPACE variable (below) to change the transfer mode.
(Useful when used with ``select_similar_poly_count.py`` first.)

[Use]

- Select the Source object first.
- Then select the Target objects.
- Run script.

[License]

Copyright 2022 Liam Collod

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
import sys

import maya.cmds as cmds


# 0: world space, 1: model space, 4: component-based, 5: topology-based.
SAMPLE_SPACE = 4
LOG_LVL = logging.INFO


def setup_logging(level):

    logger = logging.getLogger("polyTransferUVs")
    logger.setLevel(level)

    if not logger.handlers:

        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)7s][%(name)20s] // %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)

    return logger


logger = setup_logging(LOG_LVL)


class TransferError(BaseException):
    pass


class ErrorHandler(object):
    """
    Utility class to handles errors that can happen.
    Errors are stored insided and can then be raised at the end of the process.
    """
    def __init__(self):
        self.data = {}

    def add(self, source, error):
        self.data[len(self.data) + 1] = (source, error)

    def get_display_str(self):
        display_str = ""
        for error_id, error_data in self.data.items():
            error_source = error_data[0].ljust(85, ' ')
            error_type = error_data[1].__class__.__name__
            error_message = str(error_data[1]).replace('\n', '', -1)
            display_str += "{} - <{}> {} // {} \n".format(
                error_id, error_source, error_type, error_message)
        return display_str

    def log(self):

        if not self.data:
            return

        logger.error("{} Errors occured during script : \n{}".format(
            len(self.data), self.get_display_str()))

        return

    def gui_log(self):

        if not self.data:
            return

        self.log()
        raise_confirm_dialog(
            "Errors occured during script execution."
            "Please check the ScriptEditor for details."
        )
        return


def raise_confirm_dialog(message, ui_title="ERROR", ui_icon="critical"):
    """
    Raise an error dialog to the user.

    Args:
        ui_icon (str): critical, warning, info
        ui_title (str):
        message (str or Exception):
    """
    return cmds.confirmDialog(
        title=ui_title,
        message=str(message),
        button=['Confirm'],
        defaultButton='Confirm',
        cancelButton='Confirm',
        dismissString='Confirm',
        icon=ui_icon,
    )


def transfer_attributes(source_mesh, target_mesh, sample_space=4, clean=True):
    """

    Args:
        source_mesh(str):
        target_mesh(str):
        sample_space(int): Selects which space the attribute transfer is
            performed in. 0 is world space, 1 is model space,
            4 is component-based, 5 is topology-based.
        clean(bool): If True delete the history after the transfer

    """
    cmds.select([source_mesh, target_mesh])
    try:
        cmds.transferAttributes(
            sampleSpace=sample_space,
            transferUVs=2,
            transferColors=0
        )
    except Exception as excp:
        raise TransferError(
            "Transfer Attribute failed for {} : {}"
            "".format(target_mesh, excp)
        )

    if clean:
        cmds.delete(constructionHistory=True)

    logger.debug(
        "[transfer_attributes] Finished. <{}> to <{}>"
        "".format(source_mesh, target_mesh)
    )
    return


def run():

    mesh_selection_list = cmds.ls(sl=True)

    if len(mesh_selection_list) < 2 or not mesh_selection_list:
        raise_confirm_dialog(
            "Please make a selection (at least 2 objects).",
            ui_title="Warning !",
            ui_icon="warning"
        )

    source_mesh_sel = mesh_selection_list.pop(0)
    # remove the shape of the source in the list if present
    source_shape = cmds.listRelatives(source_mesh_sel, shapes=True)[0]
    try:
        mesh_selection_list.remove(source_shape)
    except ValueError:
        pass

    error_h = ErrorHandler()

    for target_mesh in mesh_selection_list:
        try:
            transfer_attributes(source_mesh=source_mesh_sel,
                                target_mesh=target_mesh,
                                sample_space=SAMPLE_SPACE,
                                clean=True)
        except TransferError as excp:
            error_h.add(target_mesh, excp)

    # select back the original selection
    mesh_selection_list.append(source_mesh_sel)
    cmds.select(mesh_selection_list)

    error_h.gui_log()  # display errors

    logger.info(
        "[run] Finished processing <{}> meshs."
        "".format(len(mesh_selection_list) - 1)
    )
    return


if __name__ == '__main__':
    run()
