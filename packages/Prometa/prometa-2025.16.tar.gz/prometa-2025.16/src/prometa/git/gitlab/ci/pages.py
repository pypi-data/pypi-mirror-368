#!/usr/bin/env python
"""
Manage the pages job.
"""

import logging

from .ci_job_manager import CIJobManager

LOGGER = logging.getLogger(__name__)


class PagesCIJobManager(CIJobManager):
    """
    This does not create the pages job. It only updates it to set the following
    fields: "artifacts", "only" and "stage".
    """

    NAME = "pages"

    def manage(self):
        pages = self.gitlab_ci.data.get(self.NAME)
        if not pages:
            return
        pages["artifacts"] = {"paths": ["public"]}
        pages["only"] = self.gitlab_ci.host.main_branches
        pages["stage"] = "deploy"


PagesCIJobManager.register(PagesCIJobManager.NAME)
