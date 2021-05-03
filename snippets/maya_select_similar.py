"""
Author: Liam Collod
Last Modified: 03/05/2021
Contact: monsieurlixm@gmail.com

[Support]
    Python 2.7+
    Maya SCRIPT

[What]
    From a selected object , find in the whole scene which geometric object has the
    same vertex number and select them.

[How]
    - Select the Source object. (transform not shape)
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

"""
# VERSION = 1.0.3

import logging

import maya.cmds as cmds

logger = logging.getLogger("maya_select_similar")
logger.setLevel(logging.INFO)


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


def get_similar_vertex_number_mesh(vertex_number_source):
    """ Find in the whole scene which geometric object has the
    same vertex number and return its transform.

    Args:
        vertex_number_source(int):
    """
    scene_mesh_list = cmds.ls(g=True, v=True)
    for scene_mesh in scene_mesh_list:
        scene_mesh = cmds.listRelatives(scene_mesh,
                                        parent=True,
                                        fullPath=True)[0]
        nvertex_mesh = cmds.polyEvaluate(scene_mesh, v=True)
        if nvertex_mesh == vertex_number_source:
            yield scene_mesh


def select_similar(source_mesh):
    """

    Args:
        source_mesh (str): maya mesh name

    """
    ntype = cmds.nodeType(source_mesh)
    if ntype != "transform":
        if ntype != "mesh":
            raise TypeError("Please select a mesh not <{}>".format(ntype))

    nvertex_source = cmds.polyEvaluate(source_mesh, v=True)
    logger.info("The original mesh has {} vertex".format(nvertex_source))

    similar_mesh_list = list(get_similar_vertex_number_mesh(nvertex_source))

    # try to remove the shape's soource
    source_shape = cmds.listRelatives(source_mesh, shapes=True)[0]
    try:
        similar_mesh_list.remove(source_shape)
    except ValueError:
        pass

    # result selection
    cmds.select(similar_mesh_list)
    cmds.select(source_mesh, af=True)

    # logger.info(cmds.ls(sl=True))
    logger.info("Number of similar meshs found & selected: {}"
                "".format(len(similar_mesh_list)))

    return


def process():

    mesh_selection_list = cmds.ls(sl=True)
    if len(mesh_selection_list) > 1 or not mesh_selection_list:
        raise_confirm_dialog("Please make only one selection",
                             ui_title="Warning",
                             ui_icon="warning")

    try:
        select_similar(mesh_selection_list[0])
    except Exception as excp:
        raise_confirm_dialog(message=excp)

    return


if __name__ == '__main__':
    process()
