#!/usr/bin/env python3
"""\
Print documentation of all recognized badges.\
"""

import logging

# Import it from badges instead of badge_manager to ensure that all subclasses
# are registered.
from ..git.gitlab.badges import BadgeManager
from ..utils import format_docstring_for_cell

LOGGER = logging.getLogger(__name__)


def document_gitlab_badges():
    """
    Document all recognized badges in a table using their corresponding manager
    class docstrings.
    """
    badges = dict(BadgeManager.list_registered_with_classes())
    print("|Name|Description|Condition|")
    print("|:- |:- |:- |")
    for name, cls in sorted(badges.items()):
        desc = format_docstring_for_cell(cls.__doc__).replace("NAME", name)
        cond = format_docstring_for_cell(cls.include.__doc__).replace("NAME", name)
        print(f"|{name}|{desc}|{cond}|")
