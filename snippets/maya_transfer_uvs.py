"""
Author: Liam Collod
Last Modified: 03/05/2021
Contact: monsieurlixm@gmail.com

[Support]
    Python 2.7+
    Maya SCRIPT

[What]
    Transfer UVs from one object to multiple objects.
    Change the SAMPLE_SPACE variable to change the transfer mode.

[How]
    - Select the Source object first.
    - Then select the Target objects.
    - Run script.

[License]
    This work is licensed under PYCO EULA Freelance License Model.

    !! By using this script  you automatically accept and agree to be
    bound by the all the terms described in the EULA. !!

    To view a copy of this license, visit
    https://mrlixm.github.io/PYCO/licenses/eula/

    This license grants the utilisation of the product on personal machines
    (1.c.) used by a single user for Commercial purposes.

    The user may not (a) share (b) distribute any of the content of the
    product, whether it has been modified or not, without an explicit
    agreement from Pyco.

    The user may modify and adapt the content of the product for himself as
    long as the above rules are respected.

[Notes]
    Usefull when used with maya_select_similar.py first.
"""
# VERSION = 1.0.3

import logging

import maya.cmds as cmds


# 0: world space, 1: model space, 4: component-based, 5: topology-based.
SAMPLE_SPACE = 4

logger = logging.getLogger("maya_transfer_uvs")
logger.setLevel(logging.INFO)


class TransferError(BaseException):
    pass


def raise_confirm_dialog(message, ui_title="ERROR", ui_icon="critical"):
    """
    Raise an error dialog to the user.

    Args:
        ui_icon (str): critical, warning, info
        ui_title (str):
        message (str or Exception):
    """
    return cmds.confirmDialog(title=ui_title,
                              message=message,
                              button=['Confirm'],
                              defaultButton='Confirm',
                              cancelButton='Confirm',
                              dismissString='Confirm',
                              icon=ui_icon, )


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
        cmds.transferAttributes(sampleSpace=sample_space,
                                transferUVs=2,
                                transferColors=0)
    except Exception as excp:
        raise TransferError(
            "Transfer Attribute failed for {} : {}"
            "".format(target_mesh, excp))

    if clean:
        cmds.delete(constructionHistory=True)

    return


def process():

    mesh_selection_list = cmds.ls(sl=True)

    if len(mesh_selection_list) < 2 or not mesh_selection_list:
        raise_confirm_dialog("Please make a selection",
                             ui_title="Warning ! ",
                             ui_icon="warning")

    source_mesh_sel = mesh_selection_list.pop(0)
    # remove the shape of the source in the list if present
    source_shape = cmds.listRelatives(source_mesh_sel, shapes=True)[0]
    try:
        mesh_selection_list.remove(source_shape)
    except ValueError:
        pass

    error_list = []
    for target_mesh in mesh_selection_list:
        try:
            transfer_attributes(source_mesh=source_mesh_sel,
                                target_mesh=target_mesh,
                                sample_space=SAMPLE_SPACE,
                                clean=True)
        except TransferError as excp:
            error_list.append(target_mesh)

    if error_list:

        error_string = ""
        for errors in error_list:
            error_string += errors + '\n'

        error_message = ("Some errors happened during script for meshs: \n {}"
                         "".format(error_string))
        logger.error(error_message)
        raise_confirm_dialog(message=error_message)

    # select back the original selection
    mesh_selection_list.append(source_mesh_sel)
    cmds.select(mesh_selection_list)

    logger.info("Finished processing <{}> meshs."
                "".format(len(mesh_selection_list)))
    return


if __name__ == '__main__':
    process()
