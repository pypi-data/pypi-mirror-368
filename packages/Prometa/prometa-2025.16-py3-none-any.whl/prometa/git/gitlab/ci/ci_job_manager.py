#!/usr/bin/env python
"""
Base class for each CI job manager.
"""

import logging

from jrai_common_mixins.registrable import Registrable

LOGGER = logging.getLogger(__name__)


class CIJobManager(Registrable):
    """
    Registrable base class for each CI job manager.
    """

    NAME = None

    def __init__(self, gitlab_ci):
        """
        Args:
            gitlab_ci:
                A GitLabCI instance.
        """
        self.gitlab_ci = gitlab_ci

    @property
    def enabled(self):
        """
        The job's name is in the ``gitlab.enabled_ci_jobs`` list in the
        configuration file.
        """
        return self.NAME is not None and self.NAME in self.gitlab_ci.project.config.get(
            "gitlab", "enabled_ci_jobs", default=[]
        )

    def manage(self):
        """
        Manage the job in the CI file according to current project conditions
        and configuration settings.
        """
