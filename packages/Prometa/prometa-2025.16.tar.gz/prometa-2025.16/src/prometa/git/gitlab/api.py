#!/usr/bin/env python3
"""
Wrapper around python-gitlab functionality.
"""


import functools
import logging
from contextlib import ExitStack

import requests
from gitlab.const import AccessLevel

from .badges import GitLabBadgesMixin
from .hooks import GitLabHooksMixin

LOGGER = logging.getLogger(__name__)


def get_access_level(value):
    """
    Get the access level from a user-supplied value.

    Args:
        value:
            A case-insensitive string corresponding to an access level constant
            in AccessLevel or an integer access level. If the value is None or
            unrecognized, the maintainer access level is returned.

    Returns:
        The integer access level.
    """
    default = AccessLevel.MAINTAINER
    if isinstance(value, str):
        try:
            return AccessLevel[value.upper()]
        except KeyError:
            LOGGER.error("Unrecognized access level: %s", value)
            return default
    elif isinstance(value, int):
        return value

    LOGGER.error("Unrecognized access level, returning %d", default)
    return default


class GitLabAPI(ExitStack, GitLabBadgesMixin, GitLabHooksMixin):
    """
    Wrapper around GitLab API via python-gitlab.
    """

    def __init__(self, host):
        """
        Args:
            host:
                A GitLabHost instance.
        """
        super().__init__()
        self.host = host

    @property
    def project(self):
        """
        The Project instance or subclass.
        """
        return self.host.project

    @functools.cached_property
    def gitlab(self):
        """
        The python-gitlab GitLab instance. It is only be accessible within this
        class's context.
        """
        glab = self.enter_context(self.project.config.gitlab)
        LOGGER.info("Authenticating with %s", glab.url)
        glab.auth()
        return glab

    def __exit__(self, typ, val, tback):
        # Clear the cached properties on exit.
        for prop in ("gitlab", "gitlab_project"):
            try:
                delattr(self, prop)
            except AttributeError:
                pass
        super().__exit__(typ, val, tback)
        if isinstance(val, requests.exceptions.RequestException):
            LOGGER.error("Failed to connect to GitLab instance API: %s", val)
            return True
        return False

    @functools.cached_property
    def gitlab_project(self):
        """
        The python-gitlab Project instance.
        """
        _host, namespace, name = self.project.git_repo.parsed_origin
        return self.gitlab.projects.get(f"{namespace}/{name}")

    @property
    def gitlab_config(self):
        """
        The gitlab of the project configuration file.
        """
        return self.project.config.get("gitlab", default={})

    def manage_description(self):
        """
        Manage the description. It will be taken from the first Package
        instance.
        """
        if not self.gitlab_config.get("update_description"):
            return
        for pkg in self.project.packages.values():
            new_desc = pkg.description
            old_desc = self.gitlab_project.description
            if new_desc != old_desc:
                LOGGER.info("Old description: %s", old_desc)
                LOGGER.info("New description: %s", new_desc)
                self.gitlab_project.description = new_desc
            return
        LOGGER.warning("No package description found.")

    def manage_merge_method(self):
        """
        Manage the merge method.
        """
        recognized = ("merge", "rebase_merge", "ff")
        method = self.gitlab_config.get("merge_method")
        if not method:
            return
        if method not in recognized:
            LOGGER.error(
                "Configured merge method (%s) is not a recognized method %s)",
                method,
                recognized,
            )
            return
        old_method = self.gitlab_project.merge_method
        if method != old_method:
            LOGGER.info("Old merge method: %s", old_method)
            LOGGER.info("New merge_method: %s", method)
            self.gitlab_project.merge_method = method

    def manage_protected_branches(self):
        """
        Manage protected branches as per the configuration file.
        """
        branch_man = self.gitlab_project.protectedbranches
        branches = {b.name: b for b in branch_man.list()}
        for name, conf in self.gitlab_config.get("protected_branches", {}).items():
            if conf is None:
                try:
                    branches[name].delete()
                    LOGGER.info("Unprotected branch: %s", name)
                except KeyError:
                    pass
            else:
                for key in ("merge", "push"):
                    conf[key] = get_access_level(conf.get(key, AccessLevel.MAINTAINER))

                try:
                    branch = branches[name]
                    expected = (
                        conf["merge"],
                        conf["push"],
                        conf.get("push_force", False),
                    )
                    if (
                        branch.merge_access_levels,
                        branch.push_access_levels,
                        branch.allow_force_push,
                    ) != expected:
                        LOGGER.info("Updating protected branch: %s", name)
                        (
                            branch.merge_access_levels,
                            branch.push_access_levels,
                            branch.allow_force_push,
                        ) = expected
                    branch.save()
                except KeyError:
                    LOGGER.info("Protecting branch: %s", name)
                    branch_man.create(
                        {
                            "name": name,
                            "allowed_to_merge": conf["merge"],
                            "allowed_to_push": conf["push"],
                            "allow_force_push": conf.get("push_force", False),
                        }
                    )

    def manage_protected_tags(self):
        """
        Manage protected tags as per the configuration file.
        """
        tag_man = self.gitlab_project.protectedtags
        tags = {t.name: t for t in tag_man.list()}
        for name, value in self.gitlab_config.get("protected_tags", {}).items():
            if value is None:
                try:
                    tags[name].delete()
                    LOGGER.info("Unprotected tag: %s", name)
                except KeyError:
                    pass
            else:
                value = get_access_level(value)
                try:
                    tag = tags[name]
                    if tag.create_access_levels != value:
                        LOGGER.info("Updating protected tag: %s", name)
                    tag.create_access_levels = value
                except KeyError:
                    LOGGER.info("Protecting tag: %s", name)
                    tag_man.create({"name": name, "create_access_level": value})

    def manage(self):
        """
        Update the repository via API calls.
        """
        self.manage_description()
        self.manage_merge_method()
        self.manage_protected_branches()
        self.manage_protected_tags()
        self.manage_hooks()
        self.manage_badges()

        self.gitlab_project.save()
