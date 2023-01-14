"""
author=Liam Collod
last_modified=09/04/2022
python>2.7

Demo script for beginners to create an interface in Maya using cmds.
Require OOP skills.

[Use]

Just run this script into maya script editor.

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

""" ---------------------------------------------------------------------------

API

Where you have all your functions that interact with your scene

"""

# to store all the pizza created by the user
PIZZA_DATABASE = []


def create_pizza(name):
    """
    Add teh given pizza to the database

    Args:
        name(str):
    """
    PIZZA_DATABASE.append(name)
    print("Pizza {} created".format(name))
    return


def add_pineapple():
    """
    Add pineapple on the latest pizza created.
    """
    # we get the last pizza added to the databse
    last_pizza = PIZZA_DATABASE[-1]
    print("Pineapple added on pizza {}".format(last_pizza))
    return


""" ---------------------------------------------------------------------------
GUI

Interface

"""


class PizzaCreatorWindow:

    NAME = "PizzaCreator"

    def __init__(self):

        # make sure we don't create 2 time the same window so delete it before
        self.delete_if_exists()

        self.window = cmds.window(self.NAME, title=self.NAME, widthHeight=(400, 400))

        self.build()

    def build(self):
        """
        We build all the interface elements in this method.
        """

        self.layout_main = cmds.rowColumnLayout(adjustableColumn=True)
        cmds.text(
            label="Welcome to the pizza creator",
            h=20,
            w=500,
            bgc=(0.204, 0.204, 0.21),
            al="left",
            fn="tinyBoldLabelFont",
            rs=False,
        )
        cmds.separator(height=10, style="none")
        cmds.text(label="Pizza Name:", al="left", h=25)
        self.txtf_pizza_name = cmds.textField(h=20, w=280, ann="Name of the Pizza")
        cmds.separator(height=10, style="none")

        self.layout_btns01 = cmds.rowColumnLayout(numberOfColumns=2)
        self.btn_cpizza = cmds.button(
            label="Create Pizza",
            command=self.create_pizza,
            h=50,
            w=150,
            bgc=(0.2, 0.2, 0.2),
        )
        self.btn_apineapple = cmds.button(
            label="Add Pineapple",
            command=self.add_pineapple,
            h=50,
            w=150,
            bgc=(0.2, 0.2, 0.2),
        )
        # end the layout_btns01
        cmds.setParent("..")

        # end the layout_main
        cmds.setParent("..")

        return

    def create_pizza(self, *args):
        """
        Here the *args is just because when the button call this method,
         it passes an argument we don't need.
        """
        # first we want to get the name of the pizza entered by the user
        pizza_name = cmds.textField(self.txtf_pizza_name, query=True, text=True)

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
            print("[create_pizza] pizza not created: " "the user didn't gave it a name")
            return

        # we call the function defined in the API section above, passing the pizza_name
        create_pizza(name=pizza_name)
        # we colour the button add pineapple in yellow
        cmds.button(self.btn_apineapple, edit=True, bgc=(0.8, 0.6, 0.1))
        return

    def add_pineapple(self, *args):
        # we call the function defined in the API section above
        add_pineapple()
        # we colour the button add pineapple to its original colour
        cmds.button(self.btn_apineapple, edit=True, bgc=(0.2, 0.2, 0.2))
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
