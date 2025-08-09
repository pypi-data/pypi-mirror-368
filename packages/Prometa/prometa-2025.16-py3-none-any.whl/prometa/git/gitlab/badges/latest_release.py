#!/usr/bin/env python3
"""
Latest release badge.
"""

from ....utils import prepend_docstrings
from .badge_manager import BadgeManager


class LatestReleaseBadgeManager(BadgeManager):
    """
    The latest tagged release on the project's GitLab host. This uses the
    built-in GitLab release badge.
    """

    NAME = "Latest Release"

    @property
    @prepend_docstrings("AND", BadgeManager.enabled)
    def include(self):
        """
        The project's GitLab CI file contains a release job.
        """
        gitlab_ci = self.project.git_host.gitlab_ci
        return gitlab_ci.path.exists() and "release_job" in gitlab_ci.load()

    @property
    def urls(self):
        host, _namespace, _name = self.project.git_repo.parsed_origin
        protocol = "https"
        link_url = f"{protocol}://{host}/%{{project_path}}/-/tags"
        image_url = f"{protocol}://{host}/%{{project_path}}/-/badges/release.svg"
        return link_url, image_url


LatestReleaseBadgeManager.register(LatestReleaseBadgeManager.NAME)
