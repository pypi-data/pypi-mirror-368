#!/usr/bin/env python
"""
Manage the release_job job.
"""

import logging

from .ci_job_manager import CIJobManager

LOGGER = logging.getLogger(__name__)


class ReleaseJobCIJobManager(CIJobManager):
    """
    Add a release job that triggers when Git release tags are pushed. The
    release tag regular expression can be set in the configuration file.
    """

    NAME = "release_job"

    def manage(self):
        regex = self.gitlab_ci.project.config.get("gitlab", "release_tag_regex")
        if regex:
            self.gitlab_ci.data[self.NAME] = {
                "image": "registry.gitlab.com/gitlab-org/release-cli:latest",
                "release": {
                    "description": "Release $CI_COMMIT_TAG",
                    "tag_name": "$CI_COMMIT_TAG",
                },
                "rules": [{"if": f"$CI_COMMIT_TAG =~ /{regex}/"}],
                "script": [f'echo "Running {self.NAME}"'],
                "stage": "release",
            }
        else:
            self.gitlab_ci.data.pop(self.NAME, None)


ReleaseJobCIJobManager.register(ReleaseJobCIJobManager.NAME)
