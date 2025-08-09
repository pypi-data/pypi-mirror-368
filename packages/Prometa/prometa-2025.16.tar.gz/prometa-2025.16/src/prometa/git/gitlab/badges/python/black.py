#!/usr/bin/env python3
"""
Black code-style badge.
"""

from ..common import get_badge_url
from .python import ToggledPythonBadgeManager


class BlackBadgeManager(ToggledPythonBadgeManager):
    """
    The Python package uses `Black`_ for code formatting.

    .. _Black: https://pypi.org/project/black/
    """

    NAME = "Black"

    @property
    def urls(self):
        link_url = "https://pypi.org/project/black/"
        image_url = get_badge_url("code style", "black", "000000")
        return link_url, image_url


BlackBadgeManager.register(BlackBadgeManager.NAME)
