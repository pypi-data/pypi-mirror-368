#!/usr/bin/env python
"""
Project class.
"""

import logging

import spdx_matcher
from spdx_license_list import LICENSES as SPDX_LICENSES

from .citation import Citation
from .codemeta.codemeta import CodeMeta
from .common import ENCODING
from .config import Config
from .git import GitHost, GitRepo
from .package import Package
from .readme import ReadmeInserter
from .utils import choose

LOGGER = logging.getLogger(__name__)


class Project:
    """
    Project class.
    """

    def __init__(self, path, **config_kwargs):
        """
        Args:
            path:
                The path to the project.

            **config_kwargs:
                Keyword arguments passed through to Config.
        """
        self.git_repo = GitRepo(path)
        self.config = Config(self.git_repo.path, **config_kwargs)
        self.git_host = GitHost.get_primary_host(self)
        self.codemeta = CodeMeta(self)
        pkgs = ((n, c(self)) for (n, c) in Package.list_registered_with_classes())
        self.packages = {n: p for (n, p) in pkgs if p.is_valid}
        LOGGER.debug(
            "Detected packages in %s: %s", self.git_repo.path, ", ".join(self.packages)
        )

    @property
    def readme_md_path(self):
        """
        The README.md path.
        """
        return self.git_repo.path / "README.md"

    @property
    def license_txt_path(self):
        """
        The path to the LICENSE.txt file.
        """
        return self.git_repo.path / "LICENSE.txt"

    @property
    def spdx_license(self):
        """
        The detected SPDX license name.
        """
        config_license = self.config.get("license")
        if config_license:
            LOGGER.info("Using license from configuration file: %s", config_license)
            if config_license not in SPDX_LICENSES:
                LOGGER.warning('"%s" is not a recognized SPDX license', config_license)
            return config_license
        path = self.license_txt_path
        LOGGER.info("Attempting to detect license from %s", path)
        try:
            detected, percent = spdx_matcher.analyse_license_text(
                path.read_text(encoding=ENCODING)
            )
        except FileNotFoundError:
            LOGGER.error("No license file found at %s", path)
            return None
        licenses = list(detected["licenses"])
        if not licenses:
            LOGGER.error("Failed to detect license in %s", path)
            return None
        lic = choose(licenses)
        if percent < 0.9:
            LOGGER.warning(
                "Detected %s license in %s but certainty is only %(0.0f) %",
                lic,
                path,
                percent * 100.0,
            )
        return lic

    @property
    def codemeta_json_path(self):
        """
        The path to the codemeta.json file.
        """
        return self.git_repo.path / "codemeta.json"

    @property
    def citation_cff_path(self):
        """
        The path to the CITATION.cff file.
        """
        return self.git_repo.path / "CITATION.cff"

    @property
    def urls(self):
        """
        A dict of URLs for the project.
        """
        urls = self.git_repo.urls
        if self.git_host:
            urls.update(self.git_host.urls)
        return urls

    def update(self):
        """
        Update project metadata.
        """
        for pkg in self.packages.values():
            pkg.update()

        if self.codemeta_json_path.exists():
            Citation(self).update()

        # This should be done before updating the README as it may change the
        # badges.
        if self.git_host:
            self.git_host.update()

        readme_inserter = ReadmeInserter(self)
        readme_inserter.update(self.readme_md_path)

    @property
    def name(self):
        """
        The project name. It will use the value in codemeta.name if it exists,
        otherwise it will use the name of the project's directory.
        """
        name = self.codemeta.name
        if name is not None:
            return name
        return self.git_repo.path.name
