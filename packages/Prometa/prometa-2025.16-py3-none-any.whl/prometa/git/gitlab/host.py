#!/usr/bin/env python
"""
Functionality for GitLab hosts.
"""

import functools
import logging

from ..host import GitHost
from .api import GitLabAPI
from .ci import GitLabCI

LOGGER = logging.getLogger(__name__)


class GitLabHost(GitHost):
    """
    Functionality for GitLab hosts.
    """

    @property
    def is_used(self):
        return bool(self.project.config.get("gitlab"))

    @functools.cached_property
    def gitlab_ci(self):
        """
        The GitLabCI instance.
        """
        return GitLabCI(self)

    @functools.cached_property
    def gitlab_api(self):
        """
        The GitLabAPI instance.
        """
        return GitLabAPI(self)

    @property
    def main_branches(self):
        """
        The main branches to which to restrict some configurations such as CI
        jobs via the "only" parameter.
        """
        return self.project.config.get("gitlab", "main_branches", default=["main"])

    @property
    def urls(self):
        host, namespace, name = self.project.git_repo.parsed_origin
        urls = {}
        if self.gitlab_ci.data.get("pages"):
            pages_fmt = self.project.config.get("gitlab", "pages_urls", host)
            if pages_fmt:
                urls["Documentation"] = pages_fmt.format(namespace=namespace, name=name)
        return urls

    def update(self):
        self.gitlab_ci.manage()
        with self.gitlab_api as api:
            api.manage()


GitLabHost.register("gitlab")
