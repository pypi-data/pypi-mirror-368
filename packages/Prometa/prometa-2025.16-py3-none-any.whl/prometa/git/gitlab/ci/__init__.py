#!/usr/bin/env python
"""
Manage the CI file.
"""

import importlib
import logging
import re

import yaml

from ....file import update_content
from .ci_job_manager import CIJobManager

LOGGER = logging.getLogger(__name__)


# Import modules to ensure that subclasses are registered.
for pkg in ("pages", "release_job", "python"):
    LOGGER.debug("Importing %s.%s", __name__, pkg)
    importlib.import_module(f".{pkg}", __name__)


class GitLabCI:
    """
    Wrapper around the gitlab-ci file.
    """

    def __init__(self, host, path=".gitlab-ci.yml"):
        """
        Args:
            host:
                A GitLabHost instance.

            path:
                The path to the gitlab-ci file, relative to the repository root
                directory.
        """
        self.host = host
        self.path = self.project.git_repo.path / path
        self._data = None

    @property
    def project(self):
        """
        The Project instance or subclass.
        """
        return self.host.project

    @property
    def data(self):
        """
        The CI configuration data.
        """
        if self._data is None:
            self._data = self.load()
        return self._data

    def load(self):
        """
        Load the file data.

        Returns:
            The loaded data, or an empty dict if the file does not exist.
        """
        try:
            with self.path.open("rb") as handle:
                return yaml.safe_load(handle)
        except FileNotFoundError:
            return {}

    def add_stages(self):
        """
        Add the list of stages for all added jobs.
        """
        recognized_stages = [".pre", "build", "test", "release", "deploy", ".post"]
        stages = set()
        for key, value in self.data.items():
            if not isinstance(value, dict):
                continue
            stage = value.get("stage")
            if stage is None:
                LOGGER.error("No stage specified for job %s in %s", key, self.path)
                continue
            stages.add(stage)
        self.data["stages"] = [stage for stage in recognized_stages if stage in stages]

    def add_tags(self):
        """
        Add runner tags. This will deduplicate tags and also ensure that jobs
        using the same tags reference each other in the YAML output.
        """
        tag_map = self.project.config.get("gitlab", "ci_tags")
        if tag_map:
            tag_map = tuple(
                (re.compile(regex), tags) for regex, tags in tag_map.items()
            )
            previous_sets = []
            for name, data in self.data.items():
                if not isinstance(data, dict):
                    continue
                collected_tags = set()
                for regex, new_tags in tag_map:
                    if regex.search(name):
                        collected_tags.update(new_tags)
                collected_tags = sorted(collected_tags)
                # PyYAML seems to only emit references when nested items refer
                # to the same instance so ensure that identical lists do.
                for prev in previous_sets:
                    if collected_tags == prev:
                        collected_tags = prev
                        break
                else:
                    previous_sets.append(collected_tags)
                self.data[name]["tags"] = collected_tags

    def get_ci_job_manager(self, name):
        """
        Get an instance of the named CIJobManager subclass.
        """
        cls = CIJobManager.get_registered(name)
        return cls(self)

    def manage(self):
        """
        Manage the configured jobs in the CI file.
        """
        for name, cls in CIJobManager.list_registered_with_classes():
            LOGGER.debug('Instantiating CIJobManager "%s": %s', name, cls)
            man = cls(self)
            if man.enabled:
                LOGGER.debug("Managing CI job: %s", name)
                man.manage()
        self.add_stages()
        self.add_tags()
        update_content(yaml.dump(self.data), self.path)


__all__ = ["GitLabCI", "CIJobManager"]
