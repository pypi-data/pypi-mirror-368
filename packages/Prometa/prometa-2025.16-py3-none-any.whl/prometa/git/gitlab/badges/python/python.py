#!/usr/bin/env python3
"""
Base class for Python badges.
"""

from .....common import NAME
from .....utils import prepend_docstrings
from ..badge_manager import BadgeManager


class PythonBadgeManager(BadgeManager):
    """
    Base class for Python badges.
    """

    @property
    def package(self):
        """
        The Python Package instance, or None if the project does not contain a
        Python package.
        """
        return self.project.packages.get("python")

    @property
    @prepend_docstrings("AND", BadgeManager.enabled)
    def include(self):
        """
        The project includes a Python package.
        """
        return bool(self.package)


class ToggledPythonBadgeManager(PythonBadgeManager):
    """
    Base class for Python badges that are toggled by adding their names to the
    ``tool.prometa.enabled_badges`` list in pyproject.toml. In general these are
    badges for which no easily verifiable condition exists.
    """

    @property
    def prometa_badge_list(self):
        """
        The list of enabled badges in the pyproject.toml's ``tool.prometa`` section.
        """
        section = self.package.get_tool_configuration(NAME.lower())
        if section:
            return section.get("enabled_badges", [])
        return []

    @property
    @prepend_docstrings("AND", PythonBadgeManager.include)
    def include(self):
        """
        NAME is included in a list named ``enabled_badges`` in the
        ``[tool.prometa]`` section of the project's pyproject.toml file, e.g.
        ``enabled_badges = ["NAME"]``.
        """
        if not super().include:
            return False
        return self.NAME in self.prometa_badge_list
