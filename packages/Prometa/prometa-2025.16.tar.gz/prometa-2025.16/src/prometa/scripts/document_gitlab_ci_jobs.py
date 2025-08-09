#!/usr/bin/env python3
"""\
Print documentation of all recognized GitLab CI jobs.\
"""

import logging

# Import it from here instead of ci_job_manager to ensure that all subclasses
# are registered.
from ..git.gitlab.ci import CIJobManager
from ..utils import format_docstring_for_cell

LOGGER = logging.getLogger(__name__)


def document_gitlab_ci_jobs():
    """
    Document all recognized CI jobs in a table using their corresponding manager
    class docstrings.
    """
    jobs = dict(CIJobManager.list_registered_with_classes())
    print("|Name|Description|Condition|")
    print("|:- |:- |:- |")
    for name, cls in sorted(jobs.items()):
        desc = format_docstring_for_cell(cls.__doc__).replace("NAME", name)
        cond = format_docstring_for_cell(cls.enabled.__doc__).replace("NAME", name)
        print(f"|{name}|{desc}|{cond}|")
