#!/usr/bin/env python
"""
CodeMeta functions.
"""

import contextlib
import json
import logging
import subprocess

from ..exception import PrometaException
from ..file import update_content
from ..python.venv import VirtualEnvironment

LOGGER = logging.getLogger(__name__)


class CodeMetaError(PrometaException):
    """
    Custom exception raised when working with CodeMeta files.
    """


# https://codemeta.github.io/user-guide/
class CodeMeta:
    """
    Read and update CodeMeta files.
    """

    def __init__(self, project):
        """
        Args:
            project:
                The project object.
        """
        self.project = project
        self._data = None

    def load(self):
        """
        Load the data from the CodeMeta file.
        """
        path = self.project.codemeta_json_path
        LOGGER.debug("Loading CodeMeta data from %s", path)
        try:
            with path.open("rb") as handle:
                self._data = json.load(handle)
                return self._data
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError) as err:
            raise CodeMetaError(err) from err

    def update_file(self):
        """
        Update the CodeMeta file with the currently loaded data. If the file
        already exists, a temporary file will be created and the merge tool will
        be used to update the existing file.
        """
        path = self.project.codemeta_json_path
        if self._data is None:
            LOGGER.warning("No new data to update %s", path)
            return
        content = json.dumps(self._data, indent=2, sort_keys=True)
        update_content(content, path)

    @property
    def data(self):
        """
        The CodeMeta data.
        """
        if self._data is None:
            self.load()
        return self._data

    @property
    def name(self):
        """
        The project name.
        """
        try:
            return self.data["name"]
        except TypeError:
            return None

    def _install_in_venv(self, venv):
        """
        Install CodeMetaPy in a Python virtual environment.

        Args:
            venv:
                An instance of VirtualEnvironment with its context currently
                open.
        """
        # TODO
        # Remove setuptools once CodeMetaPy is updated for Python > 3.12
        venv.run_pip_in_venv(
            [
                "install",
                "-U",
                "CodeMetaPy",
                "setuptools",
            ]
        )

    def _run_codemeta_in_venv(self, venv, args, **kwargs):
        """
        Run a codemeta command in the virtual environment.

        Args:
            venv:
                An instance of VirtualEnvironment with its context currently
                open.

            **kwargs:
                Keyword arguments passed through to run_python_in_venv().

        Returns:
            The return value of run_python_in_venv().
        """
        # TODO
        # Remove setuptools once CodeMetaPy is updated for Python > 3.12
        return venv.run_python_in_venv(["-m", "codemeta.codemeta", *args], **kwargs)

    def modify_codemeta_data(self, codemeta_data):
        """
        Modify the CodeMeta data. Override this method is a subclass to apply
        custom modifications.

        Args:
            codemeta_data:
                The input CodeMeta data.

        Returns:
            The possibly modified CodeMeta data.
        """
        return codemeta_data

    def update(self, version=None, cwd=None, venv=None):
        """
        Update the CodeMeta file.

        Args:
            version:
                The version to set. This is sometimes necessary to force a
                version due to SCM incrementing the version for unclean
                directories.

            cwd:
                The directory in which to run the codemeta command. If None, it
                will default to the parent directory of the target codemeta.json
                path.

            venv:
                An instance of VirtualEnvironment with the context currently
                open. If None, a new instance will be created.
        """
        codemeta_json_path = self.project.codemeta_json_path
        with contextlib.ExitStack() as stack:
            if venv is None:
                venv = stack.enter_context(
                    VirtualEnvironment(update_pip=True, inherit=False)
                )
            self._install_in_venv(venv)
            tmp_dir = venv.tmp_dir
            tmp_path = tmp_dir / codemeta_json_path.name
            if cwd is None:
                cwd = codemeta_json_path.parent

            try:
                self._run_codemeta_in_venv(
                    venv, ["--enrich", "-O", str(tmp_path)], cwd=cwd
                )
            except subprocess.CalledProcessError as err:
                LOGGER.error("Failed to update %s: %s", codemeta_json_path, err)
                return

            with tmp_path.open("rb") as handle:
                codemeta = json.load(handle)
            if version:
                codemeta["version"] = version
            codemeta = self.modify_codemeta_data(codemeta)
            codemeta_text = json.dumps(codemeta, indent=2, sort_keys=True)
            if not codemeta_text.endswith("\n"):
                codemeta_text += "\n"
            update_content(codemeta_text, codemeta_json_path)
