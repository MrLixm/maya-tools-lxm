"""
version=1.1.0
author=Liam Collod
last_modified=09/04/2022
contact=monsieurlixm@gmail.com
python>2.7
maya=?

[What]

From a selected object, find in the whole scene which geometric object has the
same vertex number and select them.

Hidden geometry is being ignored.

[Use]

- Select the Source object. (its transform, not its shape)
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


LOG_LVL = logging.INFO


def setup_logging(level):

    logger = logging.getLogger("selectSimilarPolyCount")
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


def get_similar_vertex_number_mesh(vertex_number_source):
    """ Find in the whole scene which geometric object has the
    same vertex number and return its transform.

    Only parse visible meshes.

    Args:
        vertex_number_source(int):
    """
    scene_mesh_list = cmds.ls(geometry=True, visible=True)

    for scene_mesh in scene_mesh_list:

        scene_mesh = cmds.listRelatives(
            scene_mesh,
            parent=True,
            fullPath=True
        )[0]

        nvertex_mesh = cmds.polyEvaluate(scene_mesh, v=True)

        if nvertex_mesh == vertex_number_source:
            yield scene_mesh


def select_similar(source_mesh):
    """
    Args:
        source_mesh (str): maya mesh name
    """
    ntype = cmds.listRelatives(source_mesh, shapes=True)  # type: None or str
    ntype = cmds.nodeType(ntype or source_mesh)  # type: str
    if ntype != "mesh":
        raise TypeError("Please select a mesh not <{}>".format(ntype))

    nvertex_source = cmds.polyEvaluate(source_mesh, v=True)

    logger.info(
        "[select_similar] The original mesh has {} vertex"
        "".format(nvertex_source)
    )

    similar_mesh_list = list(get_similar_vertex_number_mesh(nvertex_source))

    # try to remove the shape's source
    source_shape = cmds.listRelatives(source_mesh, shapes=True)[0]
    try:
        similar_mesh_list.remove(source_shape)
    except ValueError:
        pass

    # result selection
    cmds.select(similar_mesh_list)
    cmds.select(source_mesh, af=True)

    logger.info(
        "[select_similar] Finished. Number of similar meshs found & selected: "
        "{}".format(len(similar_mesh_list))
    )

    return


def run():

    mesh_selection_list = cmds.ls(sl=True)

    if len(mesh_selection_list) > 1 or not mesh_selection_list:
        raise_confirm_dialog(
            "Please make only one selection",
            ui_title="Warning",
            ui_icon="warning"
        )

    try:
        select_similar(mesh_selection_list[0])
    except Exception as excp:
        raise_confirm_dialog(message=excp)

    return


if __name__ == '__main__':
    run()
