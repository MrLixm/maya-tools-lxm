"""
author="Liam Collod"
version="0.1.0"
description="Export the selected reference object to a new .ma file but unload the reference and remove the namespace."
"""
import os
from contextlib import contextmanager

from maya import cmds


@contextmanager
def temporary_namespace_removal(namespace_to_remove):
    """
    To use as context to remove a given namespace then add it back once the context is finished.

    SRC: https://forums.cgsociety.org/t/removing-namespaces-from-referenced-objects/1550197/3

    Args:
        namespace_to_remove (str):
    """

    cmds.namespace(set=":")
    cmds.namespace(set=namespace_to_remove)
    cmds.namespace(rel=True)

    try:
        yield
    finally:
        cmds.namespace(set=":")
        cmds.namespace(rel=False)


def extract_namespace_from_node_path(node_path):
    """

    Args:
        node_path (str): also called "name". ex: "|assetName:bouteilleBiere01"

    Returns:
        str: namespace name only. ex: "assetName"
    """
    namespace = node_path.split(":")[0]
    namespace = namespace.lstrip("|")
    return namespace


def get_export_path():
    """
    Get the file path to export the scene to.

    For now open a dialog to ask the user. But one could automatize this to create an
    automatized path relative to the one of the currently opened scene...

    Returns:
        str or None: non-existing file path to export the scene to or None
    """
    export_path = cmds.fileDialog2(
        fileFilter="*.ma",
        dialogStyle=2,
        fileMode=0,  # any file that might not exist
        caption="Export Location",
    )  # type: list[str]
    if not export_path:
        return None
    return export_path[0]


def export_reference_as_baked():
    """
    Export the selected reference object to a new .ma file but unload the reference and remove the namespace.
    """

    node_to_export = cmds.ls(selection=True, long=True)  # type: list[str]
    if not node_to_export:
        raise ValueError("No object selected !")

    node_to_export = node_to_export[0]  # type: str

    if not cmds.referenceQuery(node_to_export, isNodeReferenced=True):
        raise TypeError(
            "Selected object {} is not a reference !".format(node_to_export)
        )

    message = "You are about to export <{}>".format(node_to_export)
    print("[export_reference_as_baked]" + message)
    result = cmds.confirmDialog(
        icon="question",  # "question", "information", "warning", "critical"
        title="Export Confirmation",
        message=message,
        button=["Continue", "Cancel"],
        defaultButton="Continue",
        cancelButton="Cancel",
        dismissString="Cancel",
    )
    if result == "Cancel":
        return

    target_path = get_export_path()
    if not target_path:
        return

    if os.path.exists(target_path):
        raise FileExistsError(
            "You can't overwrite an existing file when publishing ! {} already exists"
            "".format(target_path)
        )

    # remove the namespace while exporting then restore it
    namespace_to_remove = extract_namespace_from_node_path(node_to_export)
    with temporary_namespace_removal(namespace_to_remove):

        cmds.file(
            target_path,
            type="mayaAscii",
            exportSelected=True,
            preserveReferences=False,  # unload the reference
        )

    message = "Sucessfully exported {} to <{}>".format(node_to_export, target_path)
    print("[export_reference_as_baked]" + message)
    cmds.confirmDialog(
        icon="information",
        title="Export Finished",
        message=message,
        button=["Continue"],
        defaultButton="Continue",
        cancelButton="Continue",
        dismissString="Continue",
    )
    return


# if file directly executed
if __name__ == "__main__":

    export_reference_as_baked()
