import datetime
import json
import logging
import os
import re
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
        maya_batch_path: Path,
    ):

        self.maya_file = maya_file
        self.common_denominator = common_denominator
        self.root_substitute = root_substitute
        self.maya_batch_path = maya_batch_path

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

        # avoid conflict, make a clean env
        env["PATH"] = ""
        env.pop("_", None)
        env.pop("VIRTUAL_ENV", None)

        # network crap optimizations
        env["MAYA_DISABLE_CLIC_IPM"] = "1"
        env["MAYA_DISABLE_CIP"] = "1"
        env["MAYA_DISABLE_CER"] = "1"
        env["MAYA_DISABLE_ADP"] = "1"

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

        command = [
            str(self.maya_batch_path),
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

    def log_result(self, result: subprocess.CompletedProcess):

        if not result:
            return

        stdout_result = result.stdout.decode("utf-8")
        stdout_lines = stdout_result.split("\r\r\n")

        logged_ref_num = False

        for stdout_line in stdout_lines:

            if stdout_line.startswith("ERROR   | 2"):
                logger.error(f"<{self.identifier}> {stdout_line}")

            elif "no references in scene" in stdout_line:
                logger.info(f"<{self.identifier}> No references in scene.")

            regex_match = re.search(
                r"open_and_repath_references.+\w\d*/(\d*)", stdout_line
            )
            if regex_match and not logged_ref_num:
                logged_ref_num = True
                logger.info(
                    f"<{self.identifier}> Processed {regex_match.group(1)} references."
                )

            regex_match = re.search(
                r"save_scene_increment.+Saving(.+)\.\.\.", stdout_line
            )
            if regex_match:
                logger.info(f"<{self.identifier}> Saved to {regex_match.group(1)}")

        logger.info(f"<{self.identifier}> Finished.")
        return


def batch_directory(
    maya_files_dir: Path,
    new_root_dir: Path,
    denominator: Path,
    maya_batch_path: Path,
):
    """
    Parse the given directory to find all maya file and repath all references inside them.

    Args:
        maya_files_dir: initial directory to parse recursively for maya files.
        new_root_dir: directory path used as root for reference repathing.
        denominator:
        maya_batch_path: path to the mayabatch.exe file to use for batching.
    """

    logger.debug(
        f"Started with:\n"
        f"    maya_files_dir={maya_files_dir}\n"
        f"    new_root_dir={new_root_dir}\n"
        f"    denominator={denominator}\n"
        f"    maya_batch_path={maya_batch_path}"
    )

    maya_file_list = get_maya_files_recursively(maya_files_dir)

    logger.info(f"About to process {len(maya_file_list)} files.")

    for file_index, maya_file in enumerate(maya_file_list):

        file_batcher = FileBatcher(
            maya_file=maya_file,
            common_denominator=denominator,
            root_substitute=new_root_dir,
            maya_batch_path=maya_batch_path,
        )
        batch_result = file_batcher.execute()
        file_batcher.log_result(result=batch_result)

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
    refrepath.maya_utils.override_maya_logging()

    logger.info("Started.")

    source_maya_file = os.getenv(FileBatcher.Variables.arg_maya_file)
    source_common_denominator = os.getenv(FileBatcher.Variables.arg_denominator)
    source_root_substitute = os.getenv(FileBatcher.Variables.arg_root)

    if (
        not source_maya_file
        or not source_common_denominator
        or not source_root_substitute
    ):
        raise EnvironmentError("Missing one of the REFREPATH_ARG... variable.")

    repathed_references = refrepath.core.open_and_repath_references(
        maya_file_path=Path(source_maya_file),
        common_denominator=Path(source_common_denominator),
        root_substitute=Path(source_root_substitute),
    )

    # only save the scene if we actually edited at least one reference
    any_reference_edited = any(
        [repathed_ref.was_updated() for repathed_ref in repathed_references]
    )
    if any_reference_edited:
        refrepath.maya_utils.save_scene_increment()

    logger.info("Finished.")
    return
