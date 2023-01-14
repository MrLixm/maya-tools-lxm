"""
version=4
author="Liam Collod<monsieurlixm@gmail.com>"
dependencies=[
    "python>2.7",
    "maya~=2020",
]
description="How to create a window using maya.cmds API."
instructions=\"\"\"
    Copy and execute in Maya ScriptEditor
\"\"\"

license=\"\"\"
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
\"\"\"
"""
import logging

import maya.cmds as cmds


logger = logging.getLogger("pizza_creator")


""" ---------------------------------------------------------------------------

API

Where you have all your functions that interact with your scene. 
They must be indepent from the interface.

"""


PIZZA_DATABASE = {}
"""
To store all the pizza created by the user with their property.

Pizzas are stored as ::

    { pizzaName: { "hasPineapple": bool }, ... }
"""


def create_pizza(name):
    """
    Add the given pizza to the database

    Args:
        name(str):
    """
    PIZZA_DATABASE[name] = {}
    logger.info("Pizza <{}> created".format(name))
    return


def set_has_pineapple(pizza_name, has_pineapple):
    """
    Add pineapple on the latest pizza created.

    Args:
        pizza_name(str): name of the pizza on which to add pineapple.
        has_pineapple(bool): True to mention the pizza has pineapple.

    Raises:
        ValueError: if the given pizza_name was never creatd yet.
    """
    pizza = PIZZA_DATABASE.get(pizza_name)
    if pizza is None:
        raise ValueError("Pizza {} was not created.".format(pizza_name))

    # pizza should already be a dict, as set in create_pizza()
    pizza["hasPineapple"] = has_pineapple

    logger.info("Pizza <{}> set pineapple to {}".format(pizza_name, has_pineapple))
    return


def get_has_pineapple(pizza_name):
    """

    Args:
        pizza_name:

    Returns:
        bool: True if the pizza has pineapple
    """
    return PIZZA_DATABASE.get(pizza_name, {}).get("hasPineapple", False)


""" ---------------------------------------------------------------------------
GUI

Interface

"""


class PizzaCreatorWindow:

    NAME = "PizzaCreator"

    def __init__(self):

        # make sure we don't create 2 time the same window so delete it before
        self.delete_if_exists()

        self.window = cmds.window(self.NAME, title=self.NAME, widthHeight=(400, 500))

        self.build()
        self.update_pineapple_button()

    def build(self):
        """
        We build all the interface elements in this method.
        """

        # this layout will only have one column, that cna extend
        self.layout_main = cmds.frameLayout(
            collapsable=False,
            labelVisible=False,
            marginWidth=10,
            marginHeight=10,
        )
        cmds.text(
            label='<h1 style="color: #C97B30;">Welcome to the pizza creator<h1>',
            bgc=(255 / 255, 218 / 255, 102 / 255),
            align="center",
            font="boldLabelFont",
            recomputeSize=False,
            height=20,
        )
        cmds.separator(height=10, style="none")

        self.layout_create = cmds.rowColumnLayout(numberOfColumns=3)
        cmds.rowColumnLayout(self.layout_create, edit=True, adjustableColumn=2)
        cmds.rowColumnLayout(self.layout_create, edit=True, columnSpacing=[1, 10])
        cmds.rowColumnLayout(self.layout_create, edit=True, columnSpacing=[2, 10])
        cmds.rowColumnLayout(self.layout_create, edit=True, columnSpacing=[3, 10])
        cmds.text(label="Pizza Name", align="left")
        self.textfield_pizza_name = cmds.textField(annotation="Name of the Pizza")
        self.button_create_pizza = cmds.button(
            label="Create Pizza",
            command=self.create_pizza,
            bgc=(0.2, 0.2, 0.2),
        )
        # end layout_create
        cmds.setParent("..")

        cmds.separator(height=10, style="none")  # (belongs to layout_main)

        self.layout_list_pizza = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(self.layout_list_pizza, edit=True, adjustableColumn=1)
        cmds.text(label="Pizza List", align="center")
        cmds.separator(height=5, style="none")
        # list is created empty at the beginning !
        self.textlist_pizza = cmds.textScrollList(
            allowMultiSelection=False,
            # this creates a callback. The function is called when we change selection
            selectCommand=self.update_pineapple_button,
            height=200,
        )
        cmds.separator(height=10, style="none")
        self.button_add_pineapple = cmds.button(
            label="Add Pineapple",
            command=self.add_pineapple_to_selected,
            bgc=(0.2, 0.2, 0.2),
        )
        self.button_remove_pineapple = cmds.button(
            label="Remove Pineapple",
            command=self.remove_pineapple_to_selected,
            bgc=(0.2, 0.2, 0.2),
        )

        # end layout_list_pizza
        cmds.setParent("..")

        # end layout_main
        cmds.setParent("..")
        return

    def get_selected_pizza(self):
        """
        Get the name of the currently selected pizza in the list widget.

        Returns:
            str|None: name of the selected pizza or None
        """
        selected_pizza = cmds.textScrollList(
            self.textlist_pizza,
            query=True,
            selectItem=True,
        )
        if not selected_pizza:
            return None

        selected_pizza = selected_pizza[0]
        return selected_pizza

    def create_pizza(self, *args):
        """
        Here the *args is just because when the button call this method,
         it passes an argument we don't need.
        """
        # first we want to get the name of the pizza entered by the user
        pizza_name = cmds.textField(self.textfield_pizza_name, query=True, text=True)

        # if the user didn't fill the field we can raise an error message
        if not pizza_name:
            # display a dialog to the user
            cmds.confirmDialog(
                title="Error",
                icon="warning",
                message="You didn't gave a name to your pizza !",
                button=["Ok"],
                defaultButton="Ok",
                cancelButton="Ok",
                dismissString="Ok",
            )
            # we leave the method by calling return as we don't want to continue
            logger.warning(
                "[create_pizza] pizza not created: " "the user didn't gave it a name"
            )
            return

        # we call the function defined in the API section above, passing the pizza_name
        create_pizza(name=pizza_name)

        # as we modified the pizza database, we need to refresh the pizza list
        self.update_pizza_list()
        return

    def add_pineapple_to_selected(self, *args):

        selected_pizza = self.get_selected_pizza()
        if not selected_pizza:
            return

        set_has_pineapple(selected_pizza, True)

        # we need to trigger an update of the buttons interface, but we don't need
        # to refresh the whole list
        self.update_pineapple_button()
        return

    def remove_pineapple_to_selected(self, *args):

        selected_pizza = self.get_selected_pizza()
        if not selected_pizza:
            return

        set_has_pineapple(selected_pizza, False)

        # we need to trigger an update of the buttons interface, but we don't need
        # to refresh the whole list
        self.update_pineapple_button()
        return

    def update_pizza_list(self, *args):
        """
        Refresh the widget displaying all the pizza stored.
        """

        pizza_name_list = list(PIZZA_DATABASE.keys())

        # we store the name of the currently selected item, so we can restore it later
        selected_item = self.get_selected_pizza()

        # we remove all items, so we don't add duplicates !
        cmds.textScrollList(self.textlist_pizza, edit=True, removeAll=True)
        # add all the items
        cmds.textScrollList(self.textlist_pizza, edit=True, append=pizza_name_list)
        # and now we can select back the previously selected item
        # if it doesn't exist anymore, just nothing will happen
        if selected_item:
            cmds.textScrollList(
                self.textlist_pizza,
                edit=True,
                selectItem=selected_item,
            )
        return

    def update_pineapple_button(self, *args):
        """
        Update the visibility of the add/remove pineapple buttons depending on the selected item.
        """

        selected_pizza = self.get_selected_pizza()
        if selected_pizza:
            has_pineapple = get_has_pineapple(selected_pizza)
        else:
            has_pineapple = False

        # this whole condition can be "optimized" in 2 lines ;)
        if has_pineapple:
            cmds.button(self.button_add_pineapple, edit=True, enable=False)
            cmds.button(self.button_remove_pineapple, edit=True, enable=True)
        else:
            cmds.button(self.button_add_pineapple, edit=True, enable=True)
            cmds.button(self.button_remove_pineapple, edit=True, enable=False)

        return

    def delete_if_exists(self):

        if cmds.windowPref(self.NAME, query=True, exists=True):
            cmds.windowPref(self.NAME, remove=True)
        if cmds.window(self.NAME, query=True, exists=True):
            cmds.deleteUI(self.NAME, window=True)

        return

    def show(self):

        cmds.showWindow(self.window)
        return


def gui():
    """
    Create and show the interface to the user
    """

    mywindow = PizzaCreatorWindow()
    mywindow.show()

    return


if __name__ == "__main__":
    gui()
