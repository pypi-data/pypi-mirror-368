#!/usr/bin/env python3
"""
PyPI downloads.
"""

from .....utils import prepend_docstrings
from .python import PythonBadgeManager


class PyPIDownloadsBadgeManager(PythonBadgeManager):
    """
    Estimated number of downloads from `PyPI`_.

    .. _PyPI: https://pypi.org/
    """

    NAME = "PyPI Downloads"

    @property
    @prepend_docstrings("AND", PythonBadgeManager.include)
    def include(self):
        """
        The package exists on PyPI.
        """
        return super().include and self.package.pypi_url

    @property
    def urls(self):
        pypi_name = self.package.name
        link_url = f"https://pepy.tech/projects/{pypi_name}"
        image_url = f"https://static.pepy.tech/badge/{pypi_name}"
        return link_url, image_url


PyPIDownloadsBadgeManager.register(PyPIDownloadsBadgeManager.NAME)
