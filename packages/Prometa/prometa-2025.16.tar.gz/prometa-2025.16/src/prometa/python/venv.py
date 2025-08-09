#!/usr/bin/env python
"""
Virtual environment functions.
"""

import contextlib
import json
import logging
import pathlib
import shlex
import shutil
import subprocess
import sys
import sysconfig
import tempfile

from ..common import ENCODING

LOGGER = logging.getLogger(__name__)


class VirtualEnvironment(contextlib.ExitStack):
    """
    Context manager for temporary Python virtual environments.
    """

    def __init__(self, update_pip=False, inherit=False):
        """
        Args:
            update_pip:
                If True, update pip in the virtual environment.

            inherit:
                If True, create a .pth file to inherit packages from the parent
                environment.
        """
        super().__init__()

        self.update_pip = update_pip
        self.inherit = inherit

        self.tmp_dir = None
        self.venv_exe = None
        self.venv_dir = None
        self.venv_env_vars = {}

    @property
    def sys_exe(self):
        """
        The system Python executable.
        """
        return pathlib.Path(sys.executable).resolve()

    @property
    def uv_path(self):
        """
        The path to the uv executable, or None if it was not found.
        """
        uv_path = shutil.which("uv")
        if uv_path is not None:
            return pathlib.Path(uv_path).resolve()
        return None

    def run_cmd(self, cmd, **kwargs):
        """
        Run a command with subprocess.

        Args:
            cmd:
                The command to run, as a list.

            **kwargs:
                Keyword arguments passed through to subprocess.run.

        Returns:
            The return value of subprocess.run.
        """
        kwargs.setdefault("check", True)
        cmd = [str(w) for w in cmd]
        LOGGER.debug("Running command: %s", cmd)
        return subprocess.run(cmd, **kwargs)  # pylint: disable=subprocess-run-check

    def run_cmd_in_venv(self, cmd, **kwargs):
        """
        Run a command in the virtuel environment. This will pass the virtual
        environment's environment variables to the subprocess command.
        """
        kwargs.setdefault("env", {}).update(self.venv_env_vars)
        return self.run_cmd(cmd, **kwargs)

    def run_python_in_venv(self, args, **kwargs):
        """
        Run a Python command in the virtual environment. This will only work
        within this class' context.

        Args:
            args:
                The arguments to pass to the Python interpretter.

            **kwargs:
                Keyword arguments passed through to subprocess.run.

        Returns:
            The return value of subprocess.run.
        """
        cmd = [str(self.venv_exe), *args]
        return self.run_cmd_in_venv(cmd, **kwargs)

    def run_pip_in_venv(self, args, **kwargs):
        """
        Run a pip command in the virtual environment. This is a wrapper around
        run_python_in_venv().

        Args:
            args:
                The arguments to pass to pip.

            **kwargs:
                Keyword arguments passed through to run_python_in_venv().

        Returns:
            The return value of run_python_in_venv().
        """
        uv_path = self.uv_path
        if uv_path:
            return self.run_cmd_in_venv([uv_path, "pip", *args], **kwargs)
        return self.run_python_in_venv(["-m", "pip", *args], **kwargs)

    def _load_venv_env_vars(self):
        """
        Load environment variables from the activated virtual environment.
        """
        python_cmd = "import json; import os; print(json.dumps(dict(os.environ)))"
        sh_cmds = [
            [".", self.venv_dir / "bin/activate"],
            [self.venv_exe, "-c", python_cmd],
        ]
        sh_cmd_str = "; ".join(
            " ".join(shlex.quote(str(w)) for w in cmd) for cmd in sh_cmds
        )
        cmd = ["sh", "-c", sh_cmd_str]
        self.venv_env_vars = json.loads(subprocess.check_output(cmd))

    def __enter__(self):
        self.tmp_dir = pathlib.Path(self.enter_context(tempfile.TemporaryDirectory()))
        sys_exe = self.sys_exe
        self.venv_dir = self.tmp_dir / "venv"
        self.venv_exe = self.venv_dir / "bin" / sys_exe.name

        uv_path = self.uv_path
        if uv_path:
            cmd = [uv_path, "venv", self.venv_dir]
        else:
            cmd = [sys_exe, "-m", "venv", self.venv_dir]
        LOGGER.debug("Creating temporary virtual environment.")
        subprocess.run(cmd, check=True)

        self._load_venv_env_vars()

        if self.update_pip and not uv_path:
            LOGGER.debug("Updating pip in virtual environment.")
            self.run_pip_in_venv(["install", "-U", "pip"])

        if self.inherit:
            LOGGER.debug("Locating virtual environment's purelib directory.")
            child_purelib = (
                self.run_python_in_venv(
                    [
                        "-c",
                        'import sysconfig; print(sysconfig.get_paths()["purelib"])',
                    ],
                    stdout=subprocess.PIPE,
                )
                .stdout.decode()
                .strip()
            )
            parent_purelib = sysconfig.get_paths()["purelib"]
            pth_path = pathlib.Path(child_purelib) / "parent.pth"
            pth_path.write_text(parent_purelib, encoding=ENCODING)

        return self

    def __exit__(self, typ, value, traceback):
        self.venv_env_vars.clear()
