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
from refrepath.utils import is_backup_file
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
        arg_search = "REFREPATH_ARG_SEARCH"
        arg_replace = "REFREPATH_ARG_REPLACE"

    def __init__(
        self,
        maya_file: Path,
        search: str,
        replace: Path,
        maya_batch_path: Path,
    ):

        self.maya_file = maya_file
        self.search = search
        self.replace = replace
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
        env[self.Variables.arg_search] = str(self.search)
        env[self.Variables.arg_replace] = str(self.replace)

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
                logger.info(
                    f"<{self.identifier}> No references in scene.",
                    extra={"color": "green_faint"},
                )

            regex_match = re.search(
                r"open_and_repath_references.+\d+/(\d+)", stdout_line
            )
            if regex_match and not logged_ref_num:
                logged_ref_num = True
                logger.info(
                    f"<{self.identifier}> Processed {regex_match.group(1)} references.",
                    extra={"color": "green"},
                )

            regex_match = re.search(r"Saving backup <(.+)>", stdout_line)
            if regex_match:
                logger.info(
                    f"<{self.identifier}> Saved backup to {regex_match.group(1)}",
                    extra={"color": "green"},
                )

        logger.info(f"<{self.identifier}> Finished.")
        return


def batch_directory(
    maya_files_dir: Path,
    search: str,
    replace: Path,
    maya_batch_path: Path,
    ignore_backups: bool,
):
    """
    Parse the given directory to find all maya file and repath all references inside them.

    Args:
        maya_files_dir: initial directory to parse recursively for maya files.
        search: part of the path to replace. A regex patterns.
        replace: partial part to swap with the result of the search
        maya_batch_path: path to the mayabatch.exe file to use for batching.
        ignore_backups:
            True to make sure backup file generated by previosu refrepath runs ar enot processed
    """

    def is_not_backup(mfile: Path) -> bool:
        return not is_backup_file(mfile)

    logger.debug(
        f"Started with:\n"
        f"    maya_files_dir={maya_files_dir}\n"
        f"    search={search}\n"
        f"    replace={replace}\n"
        f"    maya_batch_path={maya_batch_path}\n"
        f"    ignore_backups={ignore_backups}"
    )

    maya_file_list = get_maya_files_recursively(maya_files_dir)
    if ignore_backups:
        prev_lens = len(maya_file_list)
        maya_file_list = list(filter(is_not_backup, maya_file_list))
        logger.debug(f"Removed {prev_lens - len(maya_file_list)} backup files.")

    logger.info(f"About to process {len(maya_file_list)} files.")

    for file_index, maya_file in enumerate(maya_file_list):

        file_batcher = FileBatcher(
            maya_file=maya_file,
            search=search,
            replace=replace,
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
    source_search = os.getenv(FileBatcher.Variables.arg_search)
    source_replace = os.getenv(FileBatcher.Variables.arg_replace)

    if not source_maya_file or not source_search or not source_replace:
        raise EnvironmentError("Missing one of the REFREPATH_ARG... variable.")

    repathed_references = refrepath.core.open_and_repath_references(
        maya_file_path=Path(source_maya_file),
        search=source_search,
        replace=Path(source_replace),
    )

    # only save the scene if we actually edited at least one reference
    any_reference_edited = any(
        [repathed_ref.was_updated() for repathed_ref in repathed_references]
    )
    if any_reference_edited:
        refrepath.maya_utils.save_scene_and_backup()

    logger.info("Finished.")
    return
