#!/usr/bin/env python3
"""
Display the Pylint score.
"""

from .python import PythonBadgeManager


class PylintBadgeManager(PythonBadgeManager):
    """
    Display the `Pylint`_ score.

    .. _Pylint: https://pylint.readthedocs.io/en/stable/
    """

    NAME = "Pylint"

    @property
    def urls(self):
        host, _namespace, _name = self.project.git_repo.parsed_origin
        protocol = "https"
        # The job names must correspond to the name of the CI job manager in ci.python.pylint.
        link_url = (
            f"{protocol}://{host}/%{{project_path}}/-/jobs/artifacts/"
            "%{default_branch}/raw/pylint/pylint.txt?job=pylint"
        )
        image_url = (
            f"{protocol}://{host}/%{{project_path}}/-/jobs/artifacts/"
            "%{default_branch}/raw/pylint/pylint.svg?job=pylint"
        )
        return link_url, image_url


PylintBadgeManager.register(PylintBadgeManager.NAME)
