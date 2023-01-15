import datetime
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

import refrepath
from refrepath.utils import get_maya_files_recursively
from refrepath import c

logger = logging.getLogger(__name__)


class FileBatcher:
    """
    Entity to represent all the data necessary to start the batch process for a single maya file.
    """

    class Variables:
        """
        Environment variable names.
        """

        arg_maya_file = "REFREPATH_ARG_MAYA_FILE"
        arg_denominator = "REFREPATH_ARG_DENOMINATOR"
        arg_root = "REFREPATH_ARG_ROOT"

    def __init__(
        self,
        maya_file: Path,
        common_denominator: Path,
        root_substitute: Path,
    ):

        self.maya_file = maya_file
        self.common_denominator = common_denominator
        self.root_substitute = root_substitute

        self.time = datetime.datetime.now()
        """
        Time at which the batch was initalized.
        """

        self.identifier = f"{self.maya_file.stem}-{self.time.strftime('%Y%m%d-%H%M%S')}"

        self._log_path = None
        self._env = None
        self._command = None

    @property
    def log_path(self) -> Path:
        """
        Path to the .log file to use for this process.
        """

        if self._log_path is not None:
            return self._log_path

        pretty_time = self.time.strftime("%Y%m%d-%H%M%S")
        log_filename = f"refrepath.batch-{self.maya_file.name}-{pretty_time}.log"
        self._log_path = self.maya_file.parent / log_filename
        return self._log_path

    @property
    def env(self) -> dict:
        """
        Environement variables configuration as a dictionary.
        """

        if self._env is not None:
            return self._env

        env = dict(os.environ)

        # refrepath specific
        env[self.Variables.arg_maya_file] = str(self.maya_file)
        env[self.Variables.arg_denominator] = str(self.common_denominator)
        env[self.Variables.arg_root] = str(self.root_substitute)

        # python
        refrepath_package = Path(refrepath.__path__[0]).parent
        python_path = env.get("PYTHON_PATH", "")
        python_path += f"{os.pathsep}{str(refrepath_package)}"
        env["PYTHONPATH"] = python_path

        # network crap optimizations
        env["MAYA_DISABLE_CLIC_IPM"] = "1"
        env["MAYA_DISABLE_CIP"] = "1"
        env["MAYA_DISABLE_CER"] = "1"
        env["MAYA_DISABLE_ADP"] = "1"

        # when script executed from pycharm or else, just by safety.
        if "VIRTUAL_ENV" in env:
            del env["VIRTUAL_ENV"]

        self._env = env
        return self._env

    @property
    def command(self) -> str:
        """
        Generate the terminal command for launching Maya.
        """

        if self._command is not None:
            return self._command

        maya_python_command = (
            "import refrepath.batch;refrepath.batch.process_session();"
        )
        maya_python_command = (
            repr(maya_python_command).lstrip('"').rstrip('"').lstrip("'").rstrip("'")
        )

        maya_batch = c.Env.get(
            c.Env.maya_batch,
            r"C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe",
        )

        command = [
            str(maya_batch),
            "-command",
            f'"python(\\"{maya_python_command}\\")"',
            "-log",
            str(self.log_path),
        ]

        command = " ".join(command)
        self._command = command
        return self._command

    def execute(self) -> Optional[subprocess.CompletedProcess]:
        """
        Create a subprocess to process and open the given maya file.
        """
        logger.info(f"<{self.identifier}> About to be processed ...")
        logger.debug(f"<{self.identifier}> Using command={self.command}")
        logger.debug(f"<{self.identifier}> Using env={json.dumps(self.env, indent=4)}")

        if c.DRYRUN:
            logger.info(f"<{self.identifier}> Returned earlier, DRYRUN=True")
            return None

        time_start = time.time()

        try:
            process_result = subprocess.run(
                self.command,
                capture_output=True,
                check=True,
                env=self.env,
            )
        except subprocess.CalledProcessError as excp:
            process_result = None
            logger.error(f"<{self.identifier}> {excp}")

        time_end = time.time()

        logger.debug(f"<{self.identifier}>    result:\n{process_result}")
        logger.info(f"<{self.identifier}> Finished in {time_end - time_start}s")
        return process_result


def batch_directory(directory_path: Path, root_substitute_path: Path):
    """
    Parse the given directory to find all maya file and repath all references inside them.

    Args:
        directory_path: initial directory to parse recursively for maya files.
        root_substitute_path: directory path used as root for reference repathing.
    """

    logger.info(
        f"Started with:\n"
        f"    parse_root_path={directory_path}\n"
        f"    root_substitute_path={root_substitute_path}"
    )

    if not c.Env.get(c.Env.maya_batch):
        logger.warning("! missing MAYA_BATCH_PATH env var. Using default value.")

    common_denominator = Path(root_substitute_path.name)

    maya_file_list = get_maya_files_recursively(directory_path)

    logger.info(f"About to process {len(maya_file_list)} files.")

    for file_index, maya_file in enumerate(maya_file_list):

        file_batcher = FileBatcher(
            maya_file=maya_file,
            common_denominator=common_denominator,
            root_substitute=root_substitute_path,
        )
        file_batcher.execute()

        logger.info(f"{file_index+1}/{len(maya_file_list)} completed.")
        continue

    logger.info("Finished.")
    return


def process_session():
    """
    Called from a maya session launched from a batch's subprocess.
    """

    import os
    from pathlib import Path
    import maya.mel
    import refrepath.maya_utils
    import refrepath.core

    # easier debugging
    maya.mel.eval("stackTrace -state on")

    source_maya_file = os.getenv(FileBatcher.Variables.arg_maya_file)
    source_common_denominator = os.getenv(FileBatcher.Variables.arg_denominator)
    source_root_substitute = os.getenv(FileBatcher.Variables.arg_root)

    if (
        not source_maya_file
        or not source_common_denominator
        or not source_root_substitute
    ):
        raise EnvironmentError("Missing one of the REFREPATH_ARG... variable.")

    refrepath.maya_utils.override_maya_logging()
    refrepath.core.open_and_repath_references(
        maya_file_path=Path(source_maya_file),
        common_denominator=Path(source_common_denominator),
        root_substitute=Path(source_root_substitute),
    )
    # TODO, save if only refs edited
    refrepath.maya_utils.save_scene_increment()
    return
