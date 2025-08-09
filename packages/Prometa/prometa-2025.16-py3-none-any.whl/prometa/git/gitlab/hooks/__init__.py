#!/usr/bin/env python
"""
Manage project hooks on GitLab.
"""

import importlib
import logging

from .hook_manager import HookManager

LOGGER = logging.getLogger(__name__)


# Import modules to ensure that subclasses are registered.
for pkg in ("software_heritage",):
    LOGGER.debug("Importing %s.%s", __name__, pkg)
    importlib.import_module(f".{pkg}", __name__)


class GitLabHooksMixin:
    """
    Mixin to handle hooks in GitLabApi class.
    """

    def get_hook_manager(self, name):
        """
        Get an instance of the named HookManager subclass.
        """
        cls = HookManager.get_registered(name)
        return cls(self)

    def manage_hooks(self):
        """
        Manage configured hooks.
        """
        for name, cls in HookManager.list_registered_with_classes():
            LOGGER.debug('Instantiating HookManager "%s": %s', name, cls)
            man = cls(self)
            if man.enabled:
                LOGGER.debug("Managing hook: %s", name)
                man.manage()


__all__ = ["GitLabHooksMixin", "HookManager"]
