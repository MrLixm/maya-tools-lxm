"""
VERSION=0.0.2

Author: Liam Collod
Last Modified: 23-01-2022

Script for Autodesk's Maya software. (Python 2+)
Export a Mash Network to an Alembic point-cloud.

[HowTo]:
- Select the Mash Network node.
- Run this script.

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
import os
import sys
import time
import webbrowser

from maya import cmds
import pymel.core as pm


def setup_logging(level):

    logger = logging.getLogger("m2p")
    logger.setLevel(level)

    if not logger.handlers:
        # create a file handler
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(logging.DEBUG)
        # create a logging format
        formatter = logging.Formatter(
            "%(asctime)s - [%(levelname)7s] %(name)38s // %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        # add the file handler to the logger
        logger.addHandler(handler)

    return logger


logger = setup_logging(logging.DEBUG)


class ParticleSystem(object):
    def __init__(self, name):

        self.name = name
        self.shape = name + "Shape"
        self.nucleus = None
        self.emitter = None

        return

    def build(self):

        sel_before = cmds.ls()

        # create the particle emitter
        self.emitter = cmds.emitter(
            type="omni",
            pos=[0, 0, 0],
            r=100,
            sro=0,
            nuv=0,
            cye="none",
            cyi=1,
            spd=1,
            srn=0,
            nsp=1,
            tsp=0,
            mxd=0,
            mnd=0,
            dx=1,
            dy=0,
            dz=0,
            sp=0,
        )
        # create the nParticle system
        nparticle = cmds.nParticle()[0]  # type: str
        cmds.rename(nparticle, self.name)
        cmds.connectDynamic(self.name, em=self.emitter)

        sel_after = cmds.ls()

        # try to find the nucleus and emitter node from the difference between
        # the before scene and the after scene. (funky yeah)
        ps_nodes = [
            x for x in sel_after if x not in set(sel_before)
        ]  # [u'emitter1', u'eve', u'eveShape', u'nucleus1']

        for pnode in ps_nodes:

            if "nucleus" in pnode:
                self.nucleus = pnode
            elif "emitter" in pnode:
                self.emitter = pnode

            continue

        if not self.nucleus:
            self.delete()
            raise ValueError("Nucleus was not found in <{}> !".format(ps_nodes))

        if not self.emitter:
            self.delete()
            raise ValueError("Emitter was not found in <{}> !".format(ps_nodes))

        logger.info(
            "[ParticleSystem][build] Finished. Created <{}> nParticle."
            "".format(self.name)
        )

        return

    def delete(self):
        """
        Delete the Particle system and every object associated to it.
        """

        pm.disconnectAttr(self.shape)

        try:
            cmds.delete(self.name)
        except Exception as excp:
            logger.warning(
                "[ParticleSystem][delete] Can't delete nParticle <{}>: {}"
                "".format(self.name, excp)
            )

        try:
            cmds.delete(self.shape)
        except Exception as excp:
            logger.warning(
                "[ParticleSystem][delete] Can't delete nParticle shape <{}>"
                "(not an issue): {}"
                "".format(self.shape, excp)
            )

        try:
            cmds.delete(self.emitter)
        except Exception as excp:
            logger.warning(
                "[ParticleSystem][delete] Can't delete emitter <{}>: {}"
                "".format(self.emitter, excp)
            )

        try:
            cmds.delete(self.nucleus)
        except Exception as excp:
            logger.warning(
                "[ParticleSystem][delete] Can't delete nucleus <{}> : {}"
                "".format(self.nucleus, excp)
            )

        logger.info("[ParticleSystem][delete] Finished for <{}>.".format(self.name))

        return

    def connect(self, source, target):
        """

        Args:
            source(str): full path of the attribute to connect (node+attr)
            target(str): attribute name relative to this object

        """

        cmds.connectAttr(source, "{}.{}".format(self.shape, target))

        logger.debug(
            "[ParticleSystem][connect] Finished with source={},target={}."
            "".format(source, target)
        )

        return

    def set_playfromcache(self, value):

        pfc_attr = "{}.playFromCache".format(self.shape)
        cmds.setAttr(pfc_attr, value)

        return

    def create_expression(self, expression):
        """

        Args:
            expression(str): expression to create.

        """

        # Had a bug were the dynamic expression was not computed if
        # the viewport was not refreshed.
        cmds.refresh()

        cmds.dynExpression(
            self.shape,
            creation=True,
            string=expression,
        )

        logger.debug(
            "[ParticleSystem][create_expression] Finished with expression="
            "<{}>.".format(expression)
        )

        return

    def create_attr(self, name, data_type):
        """

        Args:
            name(str): name of the attribute to create
            data_type(str): data type to use for the attribute

        """
        # Had a bug were the dynamic expression was not computed if
        # the viewport was not refreshed.
        cmds.refresh()

        cmds.addAttr(self.shape, ln=name, dataType=data_type, keyable=True)

        logger.debug(
            "[ParticleSystem][create_attr] Finished with name=<{}>,"
            "data_type=<{}>.".format(name, data_type)
        )

        return


def get_mash_network():
    """
    Returns:
        str: name of the mash network node
    """

    user_sel = cmds.ls(sl=True)

    if len(user_sel) > 1 or len(user_sel) == 0:
        raise ValueError("Select only one MASH network please")

    user_sel = user_sel[0]
    if not cmds.nodeType(user_sel) == "MASH_Waiter":
        raise ValueError("Selected object is not a valid MASH network.")

    return user_sel


def export_abc(meshs, path, attributes=None, frame_range=None, frs=None):
    """

    Args:
        meshs(list of string):
        path(str):
            export path with extension
        attributes(list or None):
            list of attributes to include in the export.
        frame_range(list of int or None):
            list of 2 values, the first one being the start frame
             and the last one the last frame
        frs(list of float or None):
            frame relatives samples to export

    Returns:
        str: path to the exported alembic file
    """

    cmds.refresh()  # safety refresh cause Maya you know

    abc_meshs = ""
    for mesh in meshs:
        abc_meshs += "-root {} ".format(mesh)

    abc_attrs = ""
    if attributes:
        for attr in attributes:
            abc_attrs += "-attr {} ".format(attr)

    frame_range = frame_range or [1, 1]
    frame_range = "{} {}".format(frame_range[0], frame_range[1])

    frs = ""
    if frs:
        for frs_item in frs:
            frs += "-frameRelativeSample {} ".format(frs_item)

    export_command = (
        "-frameRange {0} "
        "{1}"
        "{2}"
        "-uvWrite "
        "-writeFaceSets "
        "-worldSpace "
        "-writeVisibility "
        "-stripNamespaces "
        "-autoSubd "
        "-dataFormat ogawa "
        "{3}"
        "-file {4}"
        "".format(frame_range, frs, abc_attrs, abc_meshs, path)
    )

    try:
        cmds.AbcExport(j=export_command)
    except Exception as excp:
        raise RuntimeError(
            "Cannot export the ABC file , an other program might already"
            " use the existing file:\n\n{}"
            "".format(excp)
        )

    if not os.path.exists(path):
        raise RuntimeError(
            "The alembic <{}> was not exported. (Output does not exists)"
            "".format(os.path.basename(path))
        )

    logger.info(
        "[export_abc] Alembic exported to <{}> for meshs <{}>." "".format(path, meshs)
    )

    return path


class Scene(object):
    def __init__(self, config):
        """
        Args:
            config(dict): dictionary to configure how the scene is built.
        """

        self.psys = None  # type: ParticleSystem
        self.mashnw = None  # type: str
        self.config = config

        return

    def build(self):
        """ """

        # get the current selected mash network
        self.mashnw = get_mash_network()

        psys_name = self.mashnw + "_pointcloud"

        # create the Particle system
        self.psys = ParticleSystem(psys_name)
        self.psys.build()

        # Setup the ParticleSystem for export
        self.psys.set_playfromcache(True)
        # # connect the MashNetwrok to the Particle System
        self.psys.connect(
            source="{}.outputPoints".format(self.mashnw), target="cacheArrayData"
        )

        for attr_name, attr_data in self.config["build"]["particleSystem"].items():

            self.psys.create_attr(attr_name, attr_data["dataType"])

            if attr_data["mashAttr"]:
                expr = "{}.{} = {}.{};" "".format(
                    self.psys.shape, attr_name, self.mashnw, attr_data["mashAttr"]
                )
                self.psys.create_expression(expr)

        logger.debug("[Scene][build] Finished.")

        return

    def clean(self):
        """
        If needed revert the Maya scene before this script was executed.
        """

        self.psys.delete()

        logger.debug("[Scene][clean] Finished.")

        return

    def export(self):
        """

        Returns:
            str: alembic export path
        """
        export_path = cmds.fileDialog2(
            caption="Give an export path for the Alembic.",
            fileMode=0,
        )[
            0
        ]  # type: str

        if not export_path:
            raise InterruptedError("User canceled the alembic export operation.")

        if not export_path.endswith(".abc"):
            raise ValueError(
                "The given path <{}> doesn't ends with <.abc>" "".format(export_path)
            )

        # we export the particle system transform node
        export_abc(
            meshs=[self.psys.name],
            path=export_path,
            attributes=self.config["export"]["alembic"]["attributes"],
            frame_range=self.config["export"]["alembic"]["frame_range"],
            frs=self.config["export"]["alembic"]["frame_relative_samples"],
        )

        logger.debug("[Scene][export] Finished.")

        return export_path


def run():

    stime = time.time()

    """scene_config(dict)
    
    Configure how the scene is built and exported.
    
    [build.particleSystem](dict):
        each key is an attribute name to create
    
        rotation and scale doesn't have a corresponding mashAttr cause they are 
        automatically linked to the mash attribute of the same name.
        
        think to add them in [export.alembic.attributes]
        
    """
    scene_config = {
        "build": {
            "particleSystem": {
                "rotation": {"dataType": "vectorArray", "mashAttr": ""},
                "scale": {"dataType": "vectorArray", "mashAttr": ""},
                "objectIndex": {"dataType": "vectorArray", "mashAttr": "inIdPP"},
            },
        },
        "export": {
            "alembic": {
                "frame_range": [1, 1],
                "attributes": ["rotation", "scale", "objectIndex"],
                "frame_relative_samples": [],
            }
        },
    }

    scene = Scene(config=scene_config)
    try:
        scene.build()
        export_path = scene.export()
    finally:
        scene.clean()

    # raise a dialog to the user before endign the script
    user_choice = cmds.confirmDialog(
        title="Abc Exported",
        message="Abc was exported to:\n{}".format(export_path),
        button=["Open Folder", "Close"],
        defaultButton="Open Folder",
        cancelButton="Close",
        dismissString="Close",
    )

    if user_choice == "Open Folder":
        webbrowser.open(os.path.dirname(export_path))

    logger.info("[run] Finished in <{}>s".format(time.time() - stime))
    return


# execute script
if __name__ == "__main__":
    run()
