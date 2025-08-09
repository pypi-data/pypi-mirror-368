#!/usr/bin/env python
"""
Manage project badges on GitLab.
"""

import importlib
import logging

from .badge_manager import BadgeManager

LOGGER = logging.getLogger(__name__)


# Import modules to ensure that subclasses are registered.
for pkg in ("latest_release", "license", "pipeline_status", "python", "test_coverage"):
    LOGGER.debug("Importing %s.%s", __name__, pkg)
    importlib.import_module(f".{pkg}", __name__)


class GitLabBadgesMixin:
    """
    Mixin to handle badges in GitLabApi class.
    """

    def get_badge_manager(self, name):
        """
        Get an instance of the named BadgeManager subclass.
        """
        cls = BadgeManager.get_registered(name)
        return cls(self)

    def manage_badges(self):
        """
        Add or remove badges depending on the current repository configuration.
        """
        for name, cls in BadgeManager.list_registered_with_classes():
            LOGGER.debug('Instantiating BadgeManager "%s": %s', name, cls)
            man = cls(self)
            if man.enabled:
                LOGGER.debug("Managing badge: %s", name)
                man.manage()

    def get_markdown_badges(self):
        """
        Get an iterable over all badges as Markdown image links.
        """
        for badge in self.gitlab_project.badges.list(get_all=True):
            yield f"[![{badge.name}]({badge.rendered_image_url})]({badge.rendered_link_url})"


__all__ = ["GitLabBadgesMixin", "BadgeManager"]
