#!/usr/bin/env python
"""
Functionality for Python packages.
"""

import logging
import tomllib

import tomli_w
import tomli_w._writer

from ...common import ENCODING
from ...file import update_content
from ...python.common import get_license_classifier, get_pypi_url
from ...python.venv import VirtualEnvironment
from ..package import Package
from .codemeta import PyprojectCodeMeta

LOGGER = logging.getLogger(__name__)


def _join_names(given_names, family_names):
    """
    Join given and family names to a single string.

    Args:
        given_names:
            The given names.

        family_names:
            The family names.

    Returns:
        A string with the joined names.
    """
    if given_names and family_names:
        return f"{given_names} {family_names}"
    if given_names:
        return str(given_names)
    if family_names:
        return str(family_names)
    return None


class PythonPackage(Package):
    """
    Functionality for Python packages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pyproject_toml_data = (None, 0)

    @property
    def pyproject_toml_path(self):
        """
        The path to the pyproject.toml file.
        """
        return self.project.git_repo.path / "pyproject.toml"

    @property
    def is_valid(self):
        """
        True if the project appears to be a valid Python package.
        """
        return self.pyproject_toml_path.exists()

    @property
    def pyproject_toml_data(self):
        """
        The parsed pyproject.toml data. Internal caching is use to only reload
        the file when it is modified.
        """
        path = self.pyproject_toml_path
        try:
            mtime = path.stat().st_mtime
            if mtime > self._pyproject_toml_data[1]:
                data = tomllib.loads(path.read_text(encoding=ENCODING))
                self._pyproject_toml_data = (data, mtime)
        except FileNotFoundError:
            self._pyproject_toml_data = (None, 0)
        return self._pyproject_toml_data[0]

    def get_tool_configuration(self, tool):
        """
        Attempt to get a tool's configuration from the pyproject.tom file.

        Args:
            tool:
                The name of the tool, e.g. "black" or "isort".

        Return:
            The tool's configuration if found, else None.
        """
        return self.pyproject_toml_data.get("tool", {}).get(tool)

    @property
    def name(self):
        return self.pyproject_toml_data["project"]["name"]

    @property
    def description(self):
        return self.pyproject_toml_data["project"]["description"]

    @property
    def pypi_url(self):
        """
        The URL to the project on PyPI.
        """
        return get_pypi_url(self.name)

    def update(self):
        """
        Update Python package metadata.
        """
        LOGGER.info("Updating Python package metadata...")
        # TODO
        # Find a better way to automate version management while updating the
        # files. The issue is that prometa has to modify several files but these
        # modifications are visible to the VCS. This causes tools such as
        # setuptools-scm to miscalculate the version because it doesn't know
        # that the changes will be merged into the previous commit.
        version = self.get_version()
        self.update_pyproject_toml()
        PyprojectCodeMeta(self.project).update(version=version)

    @property
    def links(self):
        pypi_url = self.pypi_url
        if pypi_url:
            yield "Python Package Index (PyPI)", pypi_url

    def get_version(self):
        """
        Get the version of a project from its directory.

        This will create a temporary virtual environment and install the project in
        it to get the version. This ensures that VCS-versions are correctly handled.

        This should not be necessary but at the time or writing the current version
        of CodeMetaPy fails to detect versions.
        """
        project_dir = self.project.git_repo.path
        with VirtualEnvironment() as venv:
            venv.run_pip_in_venv(["install", "--no-deps", "-U", str(project_dir)])

            data = tomllib.loads(
                (project_dir / "pyproject.toml").read_text(encoding=ENCODING)
            )
            name = data["project"]["name"]
            return (
                venv.run_python_in_venv(
                    [
                        "-c",
                        f'from importlib.metadata import version; print(version("{name}"))',
                    ],
                    capture_output=True,
                )
                .stdout.decode()
                .strip()
            )

    def update_pyproject_toml(self):
        """
        Update the URLs in a pyproject.toml file.

        Args:
            project:
                The Project instance.
        """
        path = self.pyproject_toml_path
        data = tomllib.loads(path.read_text(encoding=ENCODING))

        urls = data["project"]["urls"]
        #  urls.clear()
        urls.update(self.project.git_repo.urls)
        try:
            urls.update(self.project.git_host.urls)
        except AttributeError:
            pass

        data["project"]["authors"] = [
            {
                "name": _join_names(author["given-names"], author["family-names"]),
                "email": author["email"],
            }
            for author in self.project.config.config["authors"]
        ]

        classifiers = set(
            classifier
            for classifier in data["project"].get("classifiers", [])
            if not classifier.startswith("License :: ")
        )

        spdx_id = self.project.spdx_license
        if spdx_id:
            license_classifier = get_license_classifier(spdx_id)
            if license_classifier:
                classifiers.add(license_classifier)
        else:
            LOGGER.warning("No license detected for project.")

        data["project"]["classifiers"] = sorted(classifiers)

        content = tomli_w.dumps(data, multiline_strings=True)
        update_content(content, path)
        return urls


PythonPackage.register(name="python")
