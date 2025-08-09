#!/usr/bin/env python
"""
Common Git functions.
"""

import logging
import pathlib
import subprocess

LOGGER = logging.getLogger(__name__)


class GitRepo:
    """
    Basic functionality for retrieving Git information.
    """

    def __init__(self, path, remote="origin"):
        """
        Args:
            path:
                A path to the Git repository or any non-submodule path within
                it.

            remote:
                The remote repository name to use for generating URLs.
        """
        self.path = pathlib.Path(path).resolve()
        self.path = self.top_level
        self.remote = remote
        self._origin_url = None

    def run_cmd(self, cmd):
        """
        Run a git command and return its output.

        Args:
            cmd:
                The git sub-command and arguments.

        Returns:
            The command output.
        """
        cmd = ("git", "-C", str(self.path), *cmd)
        LOGGER.debug("Running command: %s", cmd)
        return (
            subprocess.run(cmd, check=True, capture_output=True).stdout.decode().strip()
        )

    @property
    def top_level(self):
        """
        The top-level directory.
        """
        path = self.run_cmd(("rev-parse", "--show-toplevel"))
        return pathlib.Path(path).resolve()

    @property
    def remote_url(self):
        """
        The origin URL.
        """
        if self._origin_url is None:
            self._origin_url = self.run_cmd(("config", "--get", "remote.origin.url"))
        return self._origin_url

    @property
    def parsed_origin(self):
        """
        A 3-tuple of the origin's host, namespace and project name.
        """
        host, subpath = self.remote_url.split(":", 1)
        subpath = subpath.rsplit(".", 1)[0]
        namespace, name = subpath.split("/", 1)
        host = host.split("@", 1)[1]
        return host, namespace, name

    @property
    def public_url(self):
        """
        The URL for the main project page.
        """
        host, namespace, name = self.parsed_origin
        return f"https://{host}/{namespace}/{name}"

    def get_section_url(self, section):
        """
        The URL to one of the various GitLab sections, e.g. "blob/main" or
        "packages".
        """
        section = section.lstrip()
        return f"{self.public_url}/-/{section}"

    @property
    def public_git_url(self):
        """
        The publically accessible HTTPS URL.
        """
        return f"{self.public_url}.git"

    def get_main_blob_url(self, path):
        """
        Get the main branch URL to the given path.
        """
        path = path.lstrip("/")
        return self.get_section_url(f"blob/main/{path}")

    @property
    def readme_url(self):
        """
        The URL to the README.
        """
        return self.get_main_blob_url("README.md")

    @property
    def urls(self):
        """
        A dict of URLs for the project.
        """
        host, namespace, name = self.parsed_origin
        homepage = f"https://{host}/{namespace}/{name}"

        urls = {}
        urls["Homepage"] = homepage
        urls["Source"] = f"{homepage}.git"
        urls["Issues"] = f"{homepage}/issues"
        return urls
