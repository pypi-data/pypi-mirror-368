#!/usr/bin/env python3
"""
Software Heritage hook.
"""

import logging

from .hook_manager import HookManager

LOGGER = logging.getLogger(__name__)


class SoftwareHeritageHookManager(HookManager):
    """
    Hook to prompt `Software Heritage`_ to archive the project when it is
    updated.

    .. _Software Heritage: https://www.softwareheritage.org/
    """

    NAME = "Software Heritage"

    def manage(self):
        # Reset to releases_events when SoftwareHeritage updates their API.
        #  events_key = 'releases_events'
        events_key = "tag_push_events"
        url = "https://archive.softwareheritage.org/api/1/origin/save/webhook/gitlab/"

        swh_hook = None
        add = self.project.codemeta_json_path.exists()
        gproj = self.gitlab_project

        for hook in gproj.hooks.list(iterator=True):
            if hook.attributes["url"] == url:
                if add and swh_hook is None:
                    swh_hook = hook
                else:
                    LOGGER.info("Deleting SWH hook for %s.", gproj.name)
                    hook.delete()

        if add and swh_hook is None:
            LOGGER.info("Creating SWH webhook for %s", gproj.name)
            swh_hook = gproj.hooks.create({"url": url, events_key: True})

        if swh_hook:
            changed = False
            for key, value in swh_hook.attributes.items():
                if key.endswith("_events"):
                    expected_value = key == events_key
                    if value != expected_value:
                        changed = True
                        setattr(swh_hook, key, expected_value)
            if changed:
                LOGGER.info("Updating SWH hook for %s.", gproj.name)
                swh_hook.save()


SoftwareHeritageHookManager.register(SoftwareHeritageHookManager.NAME)
