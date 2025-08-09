#!/usr/bin/env python
"""
Base class for each badge manager.
"""

import logging

from jrai_common_mixins.registrable import Registrable

from .common import get_badge_url

LOGGER = logging.getLogger(__name__)


class BadgeManager(Registrable):
    """
    Registrable base class for each badge manager.
    """

    NAME = None

    def __init__(self, gitlab_api):
        """
        Args:
            gitlab_api:
                A GitLabApi instance.
        """
        self.gitlab_api = gitlab_api

    @property
    def project(self):
        """
        The Project instance.
        """
        return self.gitlab_api.project

    @property
    def gitlab_project(self):
        """
        The python-gitlab Project instance.
        """
        return self.gitlab_api.gitlab_project

    @property
    def enabled(self):
        """
        The badge's name is in the ``gitlab.enabled_badges`` list in the
        configuration file.
        """
        LOGGER.debug("Check if badge is enabled: %s", self.NAME)
        return self.NAME in self.project.config.get(
            "gitlab", "enabled_badges", default=[]
        )

    def get_badge_by_name(self, name):
        """
        Get a badge by name.

        Args:
            name:
                The name of the badge.

        Returns:
            The Badge instance, or None of not badge of the given name was
            found.
        """
        for badge in self.gitlab_project.badges.list(get_all=True):
            if badge.name == name:
                return badge
        return None

    def create_badge(self, name, link_url, image_url):
        """
        Create a new badge.

        Args:
            name:
                The badge name.

            link_url:
                The badge link URL.

            image_url:
                The badge image URL.
        """
        LOGGER.info("Creating badge: %s", name)
        self.gitlab_project.badges.create(
            {"name": name, "link_url": link_url, "image_url": image_url}
        )

    @staticmethod
    def update_badge(badge, link_url, image_url):
        """
        Update a badge if necessary.

        Args:
            badge:
                A Badge instance.

            link_url:
                The badge link URL.

            image_url:
                The badge image URL.
        """
        if badge.link_url != link_url or badge.image_url != image_url:
            LOGGER.info("Updating badge: %s", badge.name)
            badge.link_url = link_url
            badge.image_url = image_url
            badge.save()

    @staticmethod
    def delete_badge(badge):
        """
        Delete a badge.

        Args:
            badge:
                A Badge instance.
        """
        if badge is not None:
            LOGGER.info("Deleting badge: %s", badge.name)
            badge.delete()

    @property
    def include(self):
        """
        True if the condition for including this badge is met, else False. The
        configuration file determines of the badge is managed whereas this
        property determines if the badge is added or removed when the badge is
        managed.
        """
        return False

    @property
    def urls(self):
        """
        The link and image URLs for the badge.
        """
        return "https://example.com", get_badge_url("badge", "example", "ff0000")

    def manage(self):
        """
        Manage the badge.
        """
        name = self.NAME
        if name is None:
            LOGGER.error("Missing name in BadgeManager subclass: %s", self.__class__)
            return
        link_url, image_url = self.urls
        badge = self.get_badge_by_name(name)
        if self.include:
            if badge is None:
                self.create_badge(name, link_url, image_url)
            else:
                self.update_badge(badge, link_url, image_url)
        else:
            if badge is not None:
                self.delete_badge(badge)
