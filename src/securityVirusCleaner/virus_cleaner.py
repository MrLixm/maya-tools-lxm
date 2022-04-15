"""
version=2
author=Liam Collod
contributors={
    "Alan Weider": "initial script logic about what to clean"
}
last_modified=15/04/2022
python>2.7

[What]

Remove the "vaccine.py" virus from the currently openened maya scene and from
your system. This is a "harmless" virus but you don't want it to spread.

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
import abc
from abc import abstractmethod, abstractproperty
from datetime import datetime
import logging
import os.path
import pprint
import sys
import webbrowser

import maya.cmds as cmds

__all__ = [
    "VIRUSOBJECTS",
    "check_virus_exists",
    "delete_virus",
    "MainWindow"
]

# compatible with Python 2 *and* 3:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


def setup_logging(level):
    logger = logging.getLogger("virus_cleaner")
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


logger = setup_logging(logging.DEBUG)


class ErrorHandler(object):
    """
    Utility class to handles errors that can happen.
    Errors are stored insided and can then be raised at the end of the process.

    Args:
        context(str):
            usually the function name from where this instance was created
    """

    def __init__(self, context=None):
        self.data = {}
        self.context = context

    def add(self, source, error):
        """
        Args:
            source(str):
            error(Exception):
        """
        self.data[len(self.data) + 1] = (str(source), error)

    def __str__(self):
        """
        Returns:
            str: list of error formatted for display to user.
        """

        display_str = ""

        for error_id, error_data in self.data.items():
            error_source = error_data[0].ljust(85, ' ')
            error_type = error_data[1].__class__.__name__
            error_message = str(error_data[1]).replace('\n', '', -1)
            display_str += "{} - <{}> {} // {} \n".format(
                error_id, error_source, error_type, error_message)

        return display_str

    def log(self, context=None):

        if not self.data:
            return

        context = context or self.context
        context = "[{}]".format(context) if context else ""
        logger.error(
            "{} Errors occured during script {} :\n{}"
            "".format(len(self.data), context, self.__str__())
        )
        return


class BaseVirusObject(ABC):

    @abstractproperty
    def identifier(self):
        return

    @abstractproperty
    def object_type(self):
        pass

    @abstractproperty
    def exists(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def __str__(self):
        return "[{}] {} : <{}>".format(
            self.__class__.__name__.ljust(18), self.object_type,
            self.identifier
        )

    def __repr__(self):
        return self.__str__()


class VirusNode(BaseVirusObject):
    identifier = "to override"

    object_type = "maya node"

    def __init__(self):
        self.node = cmds.ls(self.identifier) or [None]
        self.node = self.node[0]  # type: str or None

    @property
    def exists(self):
        return True if self.node else False

    def delete(self):
        if not self.exists:
            return

        cmds.delete(self.node)
        logger.info(
            "[{}][delete] Deleted node <{}>."
            "".format(self.__class__.__name__, self.node)
        )
        return


class BreedGeneNode(VirusNode):
    identifier = "breed_gene"


class VaccineGeneNode(VirusNode):
    identifier = "vaccine_gene"


class VirusFile(BaseVirusObject):
    identifier = "to override"
    "A file path."

    object_type = "file on disk"

    @property
    def exists(self):
        return True if os.path.exists(self.identifier) else False

    def delete(self):
        if not self.exists:
            return

        os.remove(self.identifier)
        logger.info(
            "[{}][delete] Deleted file <{}>."
            "".format(self.__class__.__name__, self.identifier)
        )
        return


class VaccineFilePy(VirusFile):
    identifier = os.path.join(
        cmds.internalVar(userAppDir=True),
        "scripts",
        "vaccine.py"
    )


class VaccineFilePyc(VirusFile):
    identifier = os.path.join(
        cmds.internalVar(userAppDir=True),
        "scripts",
        "vaccine.pyc"
    )


class UserSetupFilePy(VirusFile):
    identifier = os.path.join(
        cmds.internalVar(userAppDir=True),
        "scripts",
        "userSetup.py"
    )


class UserSetupFilePyc(VirusFile):
    identifier = os.path.join(
        cmds.internalVar(userAppDir=True),
        "scripts",
        "userSetup.pyc"
    )


class VirusScriptJobs(BaseVirusObject):
    identifier = "scriptJobs running"

    object_type = "maya scriptJobs"

    def __init__(self):
        self.jobs = cmds.scriptJob(listJobs=True)
        self.jobs = list(filter(
            lambda job: "vaccine" in job or "leukocyte" in job,
            self.jobs
        ))
        self.identifier = self.jobs

    @property
    def exists(self):
        return True if self.jobs else False

    def delete(self):
        """
        Kill the virus jobs that might be running.
        """

        for job in self.jobs:
            job_id = job.split(":")[0]
            cmds.scriptJob(kill=int(job_id), force=True)
            logger.info(
                "[{}][delete] Deleted previously running job <{}>."
                "".format(self.__class__.__name__, job_id)
            )
            continue

        return


class VirusModule(BaseVirusObject):
    identifier = "module vaccine"

    object_type = "loaded python module"

    def __init__(self):
        self.modules = list(sys.modules.keys())
        self.modules = list(filter(lambda m: "vaccine" in m, self.modules))
        self.identifier = self.modules
        return

    @property
    def exists(self):
        return True if self.modules else False

    def delete(self):
        for module in self.modules:
            del sys.modules[module]
            logger.info(
                "[{}][delete] Deleted module <{}> from path"
                "".format(self.__class__.__name__, module)
            )

        return


VIRUSOBJECTS = [
    BreedGeneNode,
    VaccineGeneNode,
    VaccineFilePy,
    VaccineFilePyc,
    UserSetupFilePy,
    UserSetupFilePyc,
    VirusScriptJobs,
    VirusModule,
]
"""
All BaseVirusObject subclasses representing a potential security flaw to delete.
They are NOT instanced.
"""


def check_virus_exists():
    """
    Return a list of BaseVirusObject that have been confirmed to exists.
    If empty means no virus have been found.

    Returns:
        list of BaseVirusObject:
    """
    exists_list = list(map(lambda vo: vo(), VIRUSOBJECTS))
    exists_list = list(filter(lambda vo: vo.exists, exists_list))

    # if only the UserSetup file exists but none of the other virus objects,
    # means there is no infection.
    usersetupfiltered = list(map(lambda vo: isinstance(vo, (UserSetupFilePy, UserSetupFilePyc)), exists_list))
    if all(usersetupfiltered):
        exists_list = list()

    logger.debug(
        "[check_virus_exists] Found {} virus existing on scene and system."
        "".format(len(exists_list))
    )
    return exists_list


def delete_virus():
    """
    Find all virus and delete them.
    """
    errorh = ErrorHandler(context="delete_virus")

    virus_list = check_virus_exists()

    for virus in virus_list:

        try:
            virus.delete()
        except Exception as excp:
            errorh.add(virus, excp)
        continue

    logger.debug(
        "[delete_virus] Deleted {} virus objects.".format(len(virus_list))
    )
    errorh.log()
    return


class MainWindow:
    NAME = "VaccineVirusCleaner"

    def __init__(self):

        # make sure we doesn't create 2 time the same window so delete it before
        self._delete_if_exists()

        self.window = cmds.window(
            self.NAME,
            title=self.NAME,
            widthHeight=(750, 400),
            menuBar=True,
        )

        self.build_menu_bar()
        self.build()

    def _delete_if_exists(self):

        if cmds.windowPref(self.NAME, query=True, exists=True):
            cmds.windowPref(self.NAME, remove=True)
        if cmds.window(self.NAME, query=True, exists=True):
            cmds.deleteUI(self.NAME, window=True)

        return

    def build_menu_bar(self):
        """
        Build the top menubar of the window.
        Must be called after window creation but before build().
        """
        self.menu_about = cmds.menu(
            label="Options",
            parent=self.NAME,
        )
        self.menuitem_save = cmds.menuItem(
            label="Save Scene after Delete.",
            checkBox=True
        )

        self.menu_about = cmds.menu(
            label="Help",
            parent=self.NAME,
        )
        cmds.menuItem(
            label="GitHub Repo",
            command="webbrowser.open('https://github.com/MrLixm/Autodesk_Maya/tree/main/src/securityVirusCleaner')"
        )
        cmds.menuItem(
            label="Security Recommendations",
            command="webbrowser.open('https://discourse.techart.online/t/another-maya-malware-in-the-wild/12970')"
        )
        return

    def build(self):
        """
        We build all the interface elements in this method.
        """

        self.layout_main = cmds.frameLayout(
            collapsable=False,
            labelVisible=False,
            marginWidth=10,
            marginHeight=10,
        )

        _msg = """
<pre>Clean the "harmless" <em>vaccine.py</em> virus from this scene and your machine.</pre>
        """
        cmds.text(
            label=_msg,
            al='left',
            recomputeSize=True,
            wordWrap=True
        )

        # cmds.separator(height=0, style='none')

        cmds.rowColumnLayout(numberOfColumns=2, columnSpacing=[2, 5])
        self.icon_status = cmds.iconTextStaticLabel(
            style="iconOnly",
            backgroundColor=[0.5, 0.5, 0.5],
            width=15
        )
        self.txt_status = cmds.text(
            label="Not analyzed yet"
        )
        cmds.setParent('..')

        self.layout_btns01 = cmds.columnLayout(adjustableColumn=True)
        self.btn_cpizza = cmds.button(
            label="Check", command=self.check_virus_exists, h=50,
            bgc=(0.2, 0.2, 0.2)
        )
        self.btn_apineapple = cmds.button(
            label="Check and Delete", command=self.delete_viruses, h=50,
            bgc=(0.2, 0.2, 0.2)
        )
        # end the layout_btns01
        cmds.setParent('..')

        self.txt_results = cmds.scrollField(
            editable=False,
            height=150,
            backgroundColor=[0.23, 0.23, 0.23],
            highlightColor=[0, 0, 0]
        )
        # end the layout_main
        cmds.setParent('..')

        return

    def set_status(self, infected):
        """
        Args:
            infected(bool): True to specify the scene is infected.
        """

        if infected:
            txt = "Scene is infected."
            color = [0.9, 0.1, 0.1]
        else:
            txt = "No infection found."
            color = [0.1, 0.9, 0.1]

        cmds.iconTextStaticLabel(
            self.icon_status,
            edit=True,
            backgroundColor=color,
        )
        cmds.text(self.txt_status, edit=True, label=txt)
        return

    def log_message(self, msg, raw=False):
        """
        Args:
            raw(bool): if True log the message without adding additional info.
            msg(str):
        """
        logger.info("[MainWindow] " + msg)
        before = cmds.scrollField(self.txt_results, query=True, text=True)
        if raw:
            after = "{}\n{}".format(msg, before)
        else:
            after = "[{}] {}\n{}".format(
                datetime.now().strftime("%H:%M:%S"), msg, before
            )
        cmds.scrollField(self.txt_results, edit=True, text=after)
        return

    def check_virus_exists(self, *args):

        self.log_message("-" * 50, True)
        viruses = check_virus_exists()
        msg = "[check_virus_exists] No viruses found in scene."
        if viruses:
            self.set_status(True)
            msg = "[check_virus_exists] Found {} problematic objects :\n" \
                  "  ".format(len(viruses))
            msg += pprint.pformat(viruses, indent=2)[2::][:-1]
        else:
            self.set_status(False)

        self.log_message(msg)
        return viruses

    def delete_viruses(self, *args):

        viruses = self.check_virus_exists()
        if not viruses:
            return

        delete_virus()

        msg = "Deleted {} problematic objects.".format(len(viruses))
        self.log_message(msg)

        if cmds.menuItem(self.menuitem_save, query=True, checkBox=True):
            cmds.file(save=True)
            self.log_message("File saved.")

        msg = (
            "[delete_viruses] Finished. This file and your system should be "
            "clean from the virus.\n    This will not prevent it to re-appear "
            "if you open an infected file again !"
        )
        self.log_message(msg)
        return

    def show(self):

        cmds.showWindow(self.window)
        return


def run_interface():
    # launch the window when this script is executed
    mainwindow = MainWindow()
    mainwindow.show()
    return


if __name__ == '__main__':
    run_interface()
