#!/usr/bin/env python
"""
Generate a badge image with the Pylint score.
"""

import logging

from .....utils import prepend_docstrings
from ..ci_job_manager import CIJobManager

LOGGER = logging.getLogger(__name__)


class PylintCIJobManager(CIJobManager):
    """
    Add a job to get a Pylint score and save a badge with the score as an
    artifact.
    """

    # If this is changed, it must also be changed in the corresponding badge
    # URLs in badges.python.pylint.
    NAME = "pylint"

    @property
    @prepend_docstrings("OR", CIJobManager.enabled)
    def enabled(self):
        """
        The corresponding Pylint badge is enabled.
        """
        if super().enabled:
            return True
        pylint_badge_manager = self.gitlab_ci.host.gitlab_api.get_badge_manager(
            "Pylint"
        )
        return pylint_badge_manager.enabled

    def manage(self):
        if self.gitlab_ci.project.packages.get("python"):
            self.gitlab_ci.data[self.NAME] = {
                "image": "python:latest",
                "only": self.gitlab_ci.host.main_branches,
                "before_script": [
                    "pip install -U pip",
                    "pip install -U uv",
                    "uv venv venv",
                    "source venv/bin/activate",
                    "uv pip install -U pylint anybadge .",
                ],
                # Note that some lines are split to avoid Pylint warnings. The
                # missing commas are intentional.
                "script": [
                    "mkdir pylint",
                    "source venv/bin/activate",
                    "(LC_ALL=C pylint --output-format=text src | tee ./pylint/pylint.txt) || true",
                    r'pylint_score=$(sed -n "s@Your code has been rated at '
                    r'\([^/]\+\)/.*@\1@p" "./pylint/pylint.txt")',
                    'anybadge -o -l pylint -v "$pylint_score" -f ./pylint/pylint.svg '
                    "2=red 4=orange 8=yellow 10=green",
                ],
                "artifacts": {"paths": ["./pylint/"]},
                "stage": "test",
            }
        else:
            self.gitlab_ci.data.pop(self.NAME, None)


PylintCIJobManager.register(PylintCIJobManager.NAME)
