#!/usr/bin/env python3
"""
isort import sorting badge.
"""

from ..common import get_badge_url
from .python import ToggledPythonBadgeManager


class IsortBadgeManager(ToggledPythonBadgeManager):
    """
    The Python package sorts imports with `isort`_.

    .. _isort: https://pypi.org/project/isort/
    """

    NAME = "isort"

    @property
    def urls(self):
        link_url = "https://pypi.org/project/isort/"
        image_url = get_badge_url("imports", "isort", "1674b1", labelColor="ef8336")
        return link_url, image_url


IsortBadgeManager.register(IsortBadgeManager.NAME)
