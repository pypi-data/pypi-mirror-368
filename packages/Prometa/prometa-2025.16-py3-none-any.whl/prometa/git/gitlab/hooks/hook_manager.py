#!/usr/bin/env python
"""
Base class for each hook manager.
"""

import logging

from jrai_common_mixins.registrable import Registrable

LOGGER = logging.getLogger(__name__)


class HookManager(Registrable):
    """
    Registrable base class for each Hook manager.
    """

    NAME = None

    def __init__(self, gitlab_api):
        """
        Args:
            gitlab_ci:
                A GitLabCI instance.
        """
        self.gitlab_api = gitlab_api

    @property
    def project(self):
        """
        The Project instance.
        """
        return self.gitlab_api.project

    @property
    def gitlab_project(self):
        """
        The python-gitlab Project instance.
        """
        return self.gitlab_api.gitlab_project

    @property
    def enabled(self):
        """
        The hook's name is in the ``gitlab.enabled_hooks`` list in the
        configuration file.
        """
        LOGGER.debug("Check if hook is enabled: %s", self.NAME)
        return self.NAME in self.project.config.get(
            "gitlab", "enabled_hooks", default=[]
        )

    def manage(self):
        """
        Manage this badge. This should be overridden in subclasses.
        """
        LOGGER.error(
            "HookManager subclass %s does not override the manage method.",
            self.__class__,
        )
