#!/usr/bin/env python3
"""
PyPI package.
"""

from .....utils import prepend_docstrings
from ..common import get_badge_url
from .python import PythonBadgeManager


class PyPIBadgeManager(PythonBadgeManager):
    """
    The Python project's name on `PyPI`_.

    .. _PyPI: https://pypi.org/
    """

    NAME = "PyPI"

    @property
    @prepend_docstrings("AND", PythonBadgeManager.include)
    def include(self):
        """
        The package exists on PyPI.
        """
        return super().include and self.package.pypi_url

    @property
    def urls(self):
        link_url = self.package.pypi_url
        image_url = get_badge_url("PyPI", self.package.name, "006dad")
        return link_url, image_url


PyPIBadgeManager.register(PyPIBadgeManager.NAME)
