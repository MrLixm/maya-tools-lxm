"""
version=1
author=Liam Collod
last_modified=20/04/2022
python>2.7

[What]

Useful to reset a maya window that might have gone off-screeen and is not visible anymore.

[Use]

- Make sure the window is opened
- Modify the WINDOW_TO_FIND_NAME variable with the name that correspond to this window
- Run script

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

import maya.cmds as cmds

WINDOW_TO_FIND_NAME = "hypershade"


def pannel_get_window(pannel):
    """
    Args:
        pannel(str): name of an existing pannel

    Returns:
        str or None:
            window name of the pannel
    """

    if not cmds.panel(pannel, q=True, exists=True):
        return

    window = cmds.panel(pannel, q=True, control=True)
    window = window.split("|")[0]

    if cmds.window(window, q=True, exists=True):
        return window

    return


def find_window(name):
    """
    Args:
        name(str): case insensitive, possible name of a window

    Returns:
        str or None:
            example "scriptEditorPanel1Window"
    """
    name = name.lower().replace(" ", "")

    ui_list = cmds.lsUI(windows=True, panels=True)
    for ui_name in ui_list:
        ui_name_sanitize = ui_name.lower()
        if name in ui_name_sanitize and cmds.window(ui_name, q=True, exists=True):
            return ui_name
        elif name in ui_name_sanitize and cmds.panel(ui_name, q=True, exists=True):
            return pannel_get_window(ui_name)

    return None


def run():
    window = find_window(name=WINDOW_TO_FIND_NAME)
    if not window:
        cmds.confirmDialog(
            icon="warning",
            title='No window found.',
            message='No window found with name <{}>'.format(WINDOW_TO_FIND_NAME),
            button=['Ok'],
            defaultButton='Ok',
            cancelButton='Ok',
            dismissString='Ok'
        )
        return
    # reset window position
    cmds.window(window, edit=True, topLeftCorner=(0, 0))
    return


run()
