"""
Author: Liam Collod
Last Modified: 03/05/2021
Contact: monsieurlixm@gmail.com

[Support]
    Python 2.7+
    Maya SCRIPT

[What]
    - Make the shapes of a dag object have the same name as the transform (when
    they are different). Can work in hierarchy mode.

    !! UUID are used so be careful on scenes with references

[How]

    set INCLUDE_HIERARCHY variable to True if you want all the sub-children
    of your selection to be taken in account.

    - Select the source:
        This can be a mesh (not a shape)
        Multiples meshs
        Or a group (INCLUDE_HIERARCHY has to be True)(you will get an error
            but you can ignore it)
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
# VERSION = 0.0.3

import logging

import maya.cmds as cmds

logger = logging.getLogger("maya_rename_shape")
logger.setLevel(logging.INFO)


# If True all the children of the selection will also be processed.
INCLUDE_HIERARCHY = True


class ErrorHandler(object):
    """
    Utility class to handles errors that can happen.
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

        logger.info("{} Errors occured during script : \n{}".format(
            len(self.data), self.get_display_str()))

        return


def get_nodes_from_selection(include_hierarchy=True):
    """

    Args:
        include_hierarchy (bool): If True, the hierarchy for each node in the
         user selection will also be returned

    Returns:
        list of str: list of maya nodes by UUID, excluding shape nodes.
    """
    user_sel = cmds.ls(sl=True, long=True)
    if not user_sel:
        logger.error("Original selection is empty")
        return

    if not include_hierarchy:
        return nodes_list_to_uuid(user_sel)

    output_node_list = []
    for user_node in user_sel:
        child_list = get_children_hierarchy(node=user_node)
        for child in child_list:
            if child not in output_node_list:
                # don't add if its a shape
                if "shape" not in cmds.nodeType(child, inherited=True):
                    output_node_list.append(child)
        if user_node not in output_node_list:
            if "shape" not in cmds.nodeType(user_node, inherited=True):
                output_node_list.append(user_node)

    logger.debug("output_node_list = {}".format(output_node_list))
    # return nodes_list_to_uuid(output_node_list)
    return output_node_list


def get_children_hierarchy(node):
    """ From a given node name return its hierarchy
     Credit: https://gist.github.com/BigRoy/eddac6a93ad4ff233e2757c6bbccf3da

    Args:
        node(str): long name of the node

    Returns:
        list
    """
    result = set()
    children = set(cmds.listRelatives(node, fullPath=True) or [])
    while children:
        # logger.debug("child: {}".format(children))
        result.update(children)
        children = set(cmds.listRelatives(children, fullPath=True) or []) - result

    logger.debug("get_children_hierarchy returned: {}".format(list(result)))
    return list(result)


def nodes_list_to_uuid(node_list):
    """ Convert a list of node name to a list of node UUID

    Args:
        node_list(list of str):

    Returns:
        list of str: list of UUID
    """
    uuid_list = []
    for node in node_list:
        uuid_list.extend(cmds.ls(node, uuid=True))
    return uuid_list


def rename_shape(node2rename):
    """
    Args:
        node2rename(str): maya UUID or path of a node that is not a shape

    Returns:
         str: path of the renamed node.

    Raises:
        RuntimeError
    """

    # get the transform name from the uuid
    long_node_name = cmds.ls(node2rename, long=True)[0]
    shape_path = cmds.listRelatives(long_node_name,
                                    shapes=True,
                                    fullPath=True)

    if not shape_path:
        raise RuntimeError(
            "[rename_shape]: Given node <{}> doesn't have a shape."
            "".format(node2rename))

    shape_path = shape_path[0]

    if not long_node_name:
        raise RuntimeError(
            "[rename_shape]: Can't find node name from node {}"
            "".format(node2rename))

    new_name = long_node_name.split("|")[-1] + 'Shape'
    # We will rename the shape directly and not the parent transform because
    # sometimes renaming the parent transform will not rename the shape.

    # Rename the node with the transform name
    try:
        renamed_result = cmds.rename(shape_path, new_name)
    except Exception as excp:
        raise RuntimeError(
            "[rename_shape]: Can't rename node '{}' to '{}': {}"
            "".format(shape_path.ljust(85, ' '), new_name, excp))

    logger.info("[rename_shape]: node '{}' renamed to '{}'"
                "".format(shape_path.ljust(85, ' '), new_name))

    return renamed_result


def main():
    """
    Execute the script
    """
    nodes_list = get_nodes_from_selection(include_hierarchy=INCLUDE_HIERARCHY)
    error_h = ErrorHandler()

    for node in nodes_list:
        try:
            rename_result = rename_shape(node)
        except Exception as excp:
            error_h.add(node, excp)

    error_h.log()  # display errors


if __name__ == '__main__':
    main()
