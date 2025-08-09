#!/usr/bin/env python
"""
CodeMeta functions.
"""

import contextlib
import logging
import pathlib
import shutil
import tempfile
import tomllib

import tomli_w
import tomli_w._writer

from ...codemeta.codemeta import CodeMeta
from ...common import ENCODING
from ...id.orcid import get_orcid_url
from ...python.venv import VirtualEnvironment

LOGGER = logging.getLogger(__name__)


class PyprojectCodeMeta(CodeMeta):
    """
    Update CodeMeta files from pyproject.toml files.
    """

    # TODO
    # Remove once CodeMetaPy is updated.
    @contextlib.contextmanager
    def _modified_pyproject_toml(self):
        """
        Context manager to create a temporary modified pyproject.toml file that
        works around current bugs in CodeMetaPy. The origin of the problem is
        that the project metadata now returns custom objects for the "readme"
        and "license" fields while CodeMetaPy still expects these to be strings.

        Returns:
            The temporary path to the modified pyproject.toml file.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = pathlib.Path(tmp_dir)
            git_dir = self.project.git_repo.path
            shutil.copytree(git_dir, tmp_dir, dirs_exist_ok=True, symlinks=True)
            ppt_path = git_dir / "pyproject.toml"
            tmp_ppt_path = tmp_dir / ppt_path.name

            ppt_data = tomllib.loads(ppt_path.read_text(encoding=ENCODING))
            for field in ("license", "readme"):
                try:
                    del ppt_data["project"][field]
                except KeyError:
                    pass
            content = tomli_w.dumps(ppt_data, multiline_strings=True)
            tmp_ppt_path.write_text(content, encoding=ENCODING)

            yield tmp_ppt_path

    def modify_codemeta_data(self, codemeta_data):
        author_data = []
        for author in self.project.config.get("authors", default=[]):
            data = {
                "@type": "Person",
                "email": author["email"],
                "givenName": author["given-names"],
                "familyName": author["family-names"],
            }
            orcid = author.get("orcid")
            if orcid:
                data["@id"] = get_orcid_url(orcid)
            author_data.append(data)
        codemeta_data["author"] = author_data

        codemeta_data["name"] = self.project.packages["python"].pyproject_toml_data[
            "project"
        ]["name"]
        codemeta_data["maintainer"] = author_data[0]
        codemeta_data["readme"] = self.project.git_repo.readme_url

        for cont in codemeta_data.get("contributor", []):
            if all(
                cont[key] == author_data[0][key] for key in ("familyName", "givenName")
            ):
                cont.clear()
                cont.update(author_data[0])

        return codemeta_data

    def update(self, version=None, cwd=None, venv=None):
        with contextlib.ExitStack() as stack:
            if venv is None:
                venv = stack.enter_context(
                    VirtualEnvironment(update_pip=True, inherit=False)
                )
            cwd = stack.enter_context(self._modified_pyproject_toml()).parent
            #  cwd = self.project.git_repo.path
            # Install the package to ensure that all metadata is detected (e.g.
            # script descriptions).
            venv.run_pip_in_venv(["install", "-U", "-e", str(cwd)])
            super().update(version=version, cwd=cwd, venv=venv)
