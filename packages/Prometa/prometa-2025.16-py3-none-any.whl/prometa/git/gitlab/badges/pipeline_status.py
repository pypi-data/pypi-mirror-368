#!/usr/bin/env python3
"""
Pipeline status badge.
"""

from ....utils import prepend_docstrings
from .badge_manager import BadgeManager


class PipelineStatusBadgeManager(BadgeManager):
    """
    The current pipeline status on the project's GitLab host. This uses the
    built-in GitLab pipeline badge.
    """

    NAME = "Pipeline Status"

    @property
    @prepend_docstrings("AND", BadgeManager.enabled)
    def include(self):
        """
        The GitLab CI configuration file exists.
        """
        return self.project.git_host.gitlab_ci.path.exists()

    @property
    def urls(self):
        host, _namespace, _name = self.project.git_repo.parsed_origin
        protocol = "https"
        link_url = (
            f"{protocol}://{host}/%{{project_path}}/-/commits/%{{default_branch}}"
        )
        image_url = f"{protocol}://{host}/%{{project_path}}/badges/%{{default_branch}}/pipeline.svg"
        return link_url, image_url


PipelineStatusBadgeManager.register(PipelineStatusBadgeManager.NAME)
