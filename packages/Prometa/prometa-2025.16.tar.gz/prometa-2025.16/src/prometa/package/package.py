#!/usr/bin/env python
"""
Base class for managing third-party packages.
"""

from jrai_common_mixins.registrable import Registrable


class Package(Registrable):
    """
    Base class for managing third-party packages.
    """

    def __init__(self, project):
        """
        Args:
            project:
                A Project instance.
        """
        super().__init__()
        self.project = project

    @property
    def is_valid(self):
        """
        True if the project appears to be a valid package of this type, else
        False.
        """
        return False

    def update(self):
        """
        Update package metadata such as versions, source URLs, etc.
        """

    @property
    def name(self):
        """
        The package name.
        """
        return None

    @property
    def description(self):
        """
        The package description.
        """
        return None

    @property
    def links(self):
        """
        An iterable of name-URL pairs to create relevant package links in the
        README.
        """
        return []
