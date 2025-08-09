#!/usr/bin/env python
"""
Register Python package.
"""

import logging

from ..ci_job_manager import CIJobManager

LOGGER = logging.getLogger(__name__)


class RegisterPythonPackageCIJobManager(CIJobManager):
    """
    Add a job to build and register a Python package if the project contains
    one, or remove the job it is exists but the project does not contain a
    Python package.
    """

    NAME = "register_python_package"

    def manage(self):
        # Remove the job with the old name.
        # TODO: remove later
        old_name = "register_pip_pkg"
        self.gitlab_ci.data.pop(old_name, None)

        if self.gitlab_ci.project.packages.get("python"):
            self.gitlab_ci.data[self.NAME] = {
                "image": "python:latest",
                "only": self.gitlab_ci.host.main_branches,
                "script": [
                    "pip install build twine",
                    "python -m build",
                    "TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token "
                    "python -m twine upload --repository-url "
                    "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi "
                    "dist/*",
                ],
                "stage": "deploy",
            }
        else:
            self.gitlab_ci.data.pop(self.NAME, None)


RegisterPythonPackageCIJobManager.register(RegisterPythonPackageCIJobManager.NAME)
