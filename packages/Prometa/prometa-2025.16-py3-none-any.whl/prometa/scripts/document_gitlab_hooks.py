#!/usr/bin/env python3
"""\
Print documentation of all recognized hooks.\
"""

import logging

# Import it from badges instead of hooks_manager to ensure that all subclasses
# are registered.
from ..git.gitlab.hooks import HookManager
from ..utils import format_docstring_for_cell

LOGGER = logging.getLogger(__name__)


def document_gitlab_hooks():
    """
    Document all recognized hooks in a table using their corresponding manager
    class docstrings.
    """
    hooks = dict(HookManager.list_registered_with_classes())
    print("|Name|Description|Condition|")
    print("|:- |:- |:- |")
    for name, cls in sorted(hooks.items()):
        desc = format_docstring_for_cell(cls.__doc__).replace("NAME", name)
        cond = format_docstring_for_cell(cls.enabled.__doc__).replace("NAME", name)
        print(f"|{name}|{desc}|{cond}|")
