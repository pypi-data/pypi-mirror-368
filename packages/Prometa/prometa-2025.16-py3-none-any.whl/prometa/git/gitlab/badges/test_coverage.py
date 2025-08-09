#!/usr/bin/env python3
"""
Test coverage badge.
"""

from ....utils import prepend_docstrings
from .badge_manager import BadgeManager


class TestCoverageBadgeManager(BadgeManager):
    """
    Display the currently configured `test coverage`_ results.

    .. _test coverage: https://docs.gitlab.com/ci/testing/code_coverage/
    """

    NAME = "Test Coverage"

    @property
    @prepend_docstrings("AND", BadgeManager.enabled)
    def include(self):
        """
        The project's GitLab CI file contains test jobs with coverage fields.
        """
        gitlab_ci = self.project.git_host.gitlab_ci
        if not gitlab_ci.path.exists():
            return False
        data = gitlab_ci.load()
        for key, value in data.items():
            if key.lower().startswith("test") and value.get("coverage"):
                return True
        return False

    @property
    def urls(self):
        host, _namespace, _name = self.project.git_repo.parsed_origin
        protocol = "https"
        link_url = f"{protocol}://{host}/%{{project_path}}"
        image_url = f"{protocol}://{host}/%{{project_path}}/badges/%{{default_branch}}/coverage.svg"
        return link_url, image_url


TestCoverageBadgeManager.register(TestCoverageBadgeManager.NAME)
