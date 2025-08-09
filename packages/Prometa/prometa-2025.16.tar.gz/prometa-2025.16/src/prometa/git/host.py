#!/usr/bin/env python
"""
Base class for Git hosts.
"""

import logging

from jrai_common_mixins.registrable import Registrable

LOGGER = logging.getLogger(__name__)


class GitHost(Registrable):
    """
    Base class for Git hosts.
    """

    def __init__(self, project):
        super().__init__()
        self.project = project

    @classmethod
    def get_primary_host(cls, project):
        """
        Get the primary Git host of a project.

        Args:
            project:
                A Project instance.

        Returns:
            A GitHost subclass instance, or None if no host was found.
        """
        for name, subcls in cls.list_registered_with_classes():
            LOGGER.debug("Checking if primary host is %s", name)
            host = subcls(project)
            if host.is_used:
                return host
        return None

    @property
    def is_used(self):  # pylint: disable=unused-argument
        """
        Check if the configuration indicates that this project uses this host.

        Args:
            project:
                A Project instance.

        Returns:
            True if the project is configured to use this host, else False.
        """
        return False

    @property
    def urls(self):
        """
        A dict of URLs specific to this host.
        """
        return {}

    def update(self):
        """
        Update the host via metadata files and/or API calls. This should handle
        CI, hooks, badges, etc.
        """
