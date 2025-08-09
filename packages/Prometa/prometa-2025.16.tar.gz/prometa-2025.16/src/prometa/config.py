#!/usr/bin/env python
"""
Configuration.
"""


import logging
import os
import pathlib
import shlex

import gitlab
import yaml
from xdg.BaseDirectory import xdg_config_dirs

from .common import ENCODING, NAME
from .exception import PrometaException

LOGGER = logging.getLogger(__name__)
CONFIG_FILE = f"{NAME}.yaml"

CONFIG_EXAMPLE = """
# A list of authors. They will appear in various files (e.g. pyproject.toml,
# codemeta.json, CITATIONS.cff).
authors:
    # Given names (required)
  - given-names: John

    # Family names (required)
    family-names: Doe

    # Email (optional)
    email: john.doe@example.com

    # Affiliation (optional)
    affiliation: Example Institute

    # ORCID identifier (optional)
    orcid: XXXX-XXXX-XXXX-XXXX

    # HAL Open Science identifier (optional)
    hal: XXXXXXX

# If true, create missing CITATIONS.cff files.
citations_cff: true

# GitLab settings (optional)
gitlab:
  # Prometa uses python-gitlab to manage GitLab hooks that push code to other
  # open repositories (currently only Software Heritage). python-gitlab requires
  # both a configuration file and the name of the section in the configuration
  # file to use for a given project. For details, see the documentation:
  #
  # https://python-gitlab.readthedocs.io/en/stable/cli-usage.html#cli-configuration
  #
  # python-gitlab configuration file:
  config: path/to/python-gitlab.cfg

  # The section of the python-gitlab configuration file to use when retrieving
  # GitLab project data.
  section: somewhere

  # If true, update the project description.
  update_description: true

  # Set the merge policy (merge, rebase_merge, ff).
  merge_method: ff

  # Configure protect branches. The key is the branch name and the value is
  # either a dict or null. Null values will unprotect the corresponding branch.
  # Dict values contain the following keys to configure how the branch is
  # protected:
  #
  #   merge: who is allowed to merge
  #   push: who is allowed to push and merge
  #   push_force: a boolean indicating if force push is allowed
  #
  # merge and push_and_merge accept either an integer access level or any of the
  # constants defined in gitlab.confg.AccessLevel:
  # https://python-gitlab.readthedocs.io/en/stable/api/gitlab.html#gitlab.const.AccessLevel
  protected_branches:
      main:
          merge: maintainers
          push: maintainers
          push_force: false

  # Configure protected tags. The key is the tag string and the value is the
  # access level or null. Null values will unproctect the tag. Access level
  # values are the same as those for protected branches.
  projected_tags:
      "v*": maintainers

  # Some CI jobs such as updating GitLab pages and registering packages should
  # only be done on specific main branches. These can be configured here.
  main_branches:
      - main

  # If true, update project hooks.
  update_hooks: false

  # Configure various badges for GitLab projects. Enabled badges will be
  # created, updated and deleted according to specific conditions. For example,
  # PyPI downloads will only be created if a pyproject.toml file exists and the
  # corresponding project exists on PyPI.
  #
  # Please consult the badges documentation in the README or examing the code in
  # prometa.git.gitlab.badges for more information on supported badges. Please
  # feel free to suggest new badges by opening an issue or by emailing the
  # maintainer directly.
  #
  # Example:
  enabled_badges:
      - Pipeline Status
      - License
      - PyPI
      - PyPI Downloads
      - Hatch

  # Configure which CI jobs are managed.
  enabled_ci_jobs:
      - pages
      - register_python_package
      - release_job

  # Configure which hooks are enabled.
  enabled_hooks:
      - Software Heritage

  # Map GitLab hosts to their corresponding GitLab Pages URL formats. This map
  # will be used to generate documentation links when a "pages" job is detected
  # in the CI configuration file. The namespace and name parameters correspond
  # to those of the GitLab project.
  pages_urls:
    gitlab.com: "https://{namespace}.gitlab.io/{name}"

  # The regular expression for matching release tags. If given, a CI release job
  # will be created for tags that match this pattern. Omit this or set it to
  # null to disable release jobs.
  release_tag_regex: "^v."

  # Configure tags for GitLab CI jobs. This is a mapping of Python regular
  # expressions to lists of tags. Jobs that match the regular expressions will
  # be tagged with the corresponding tags. If multiple regular expressions match
  # a job then it will accumulate the tags.
  #
  # To apply the same tags to all jobs, use the regular expression ".".
  ci_tags:
      ".":
        - tag1
        - tag2
        - tag3

# By default, Prometa will attempt to detect each project's license using the
# spdx-matcher Python package. In some cases the detection fails (e.g. GPL v2
# and GPL v2-only use the same license text). This option can be set to an SPDX
# license identifier (https://spdx.org/licenses/) to force a particular license
# when the detection fails. If null or an empty strign then it will be ignored.
#
# Note that it will not download a new license file or modify the existing
# license file.
license: null

# The utility to use when merging changes. It must accept two file paths (the
# modified file and the original) and return non-zero exit status to indicate an
# error or abort.
merger: vimdiff


# The README interpolator can insert command output into the README. To prevent
# arbitrary command execution, Prometa will prompt the user to confirm a command
# before it is executed. This prompt can be surpressed for trusted READMEs by
# setting the following to true.
trust_commands: false
""".strip()


class ConfigError(PrometaException):
    """
    Custom error raised by the Config class.
    """


def _nested_values(data):
    """
    A generator over all nested values in a dict.
    """
    if not isinstance(data, dict):
        yield data
        return
    for value in data.values():
        if isinstance(value, dict):
            yield from _nested_values(value)
        else:
            yield value


def _nested_update(old_data, new_data, origin, new_path):
    """
    Updated nested values in a configuration dict recursively.

    Args:
        old_data:
            The dict to update in place.

        new_data:
            The data to add to old_dict.

        origin:
            A dict of the same layout as old_data but the values are updated
            with the filenames that provided them.

        new_path:
            The path from which new_data was loaded.
    """
    for key, new_value in new_data.items():
        old_value = old_data.get(key)
        if isinstance(new_value, dict) and isinstance(old_value, dict):
            _nested_update(old_value, new_value, origin[key], new_path)
        else:
            old_data[key] = new_value
            origin[key] = new_path


class Config:
    """
    Common non-derivable configuration.
    """

    def __init__(self, proj_path, custom_config_paths=None, use_xdg=True, **overrides):
        """
        Args:
            proj_path:
                The project path.

            custom_config_paths:
                An iterable over custon configuration file paths to use in
                addition to the standard configuration files that Prometa
                normally detects.

            use_xdg:
                If True, search for configuration files in standard XDG
                configuration directories. These files will be given the lowest
                priority.

            **overrides:
                Custom run-time overrides that take precedence over values in
                all discovered configuration files.
        """
        self.proj_path = pathlib.Path(proj_path).resolve()
        if not custom_config_paths:
            custom_config_paths = []
        self.custom_config_paths = [
            pathlib.Path(path).resolve() for path in custom_config_paths
        ]
        self._config = None
        self._origin = None
        self.use_xdg = use_xdg
        self.overrides = overrides

    @property
    def possible_config_paths(self):
        """
        A generator over the possible configuration file paths. Custom paths are
        yielded first, in the order they were given. Next the possible visible
        and hidden configuration paths in the current project directory and all
        of its parent directories are yielded, starting with the project
        directory and moving up to the root directory. Finally, if use_xdg is
        True, the standard XDG configuration directories are yielded, again in
        the standard order.

        The generator does not check if the paths exist but it will omit
        duplicate paths.
        """
        yielded = set()
        for path in self.custom_config_paths:
            if path not in yielded:
                yield path
                yielded.add(path)
        dir_path = self.proj_path
        while True:
            for fname in (CONFIG_FILE, f".{CONFIG_FILE}"):
                path = (dir_path / fname).resolve()
                if path not in yielded:
                    yield path
                    yielded.add(path)
            next_dir_path = dir_path.parent
            if dir_path != next_dir_path:
                dir_path = next_dir_path
            else:
                break
        if self.use_xdg:
            for config_dir in xdg_config_dirs:
                path = pathlib.Path(config_dir) / NAME / CONFIG_FILE
                if path not in yielded:
                    yield path
                    yielded.add(path)

    @property
    def config_paths(self):
        """
        A generator over existing configuration paths. It is a wrapper around
        possible_config_paths that checks for and logs existence.
        """
        for path in self.possible_config_paths:
            if path.exists():
                yield path

    @property
    def config(self):
        """
        The configuration file object. If None, there is no configuration file.

        Raises:
            ConfigError:
                One of the configuration files failed to load.
        """
        if self._config is None:
            configs = []
            for path in self.config_paths:
                LOGGER.info("Loading configuration file: %s", path)
                try:
                    with path.open("r", encoding=ENCODING) as handle:
                        data = yaml.safe_load(handle)
                except (yaml.YAMLError, OSError) as err:
                    raise ConfigError(f"Failed to load {path}: {err}") from err
                configs.append((path, data))
            final_config = {}
            origin = {}
            for path, config in reversed(configs):
                _nested_update(final_config, config, origin, path)
            _nested_update(final_config, self.overrides, origin, "overrides")
            self._config = final_config
            self._origin = origin
        return self._config

    def get(self, *keys, default=None):
        """
        Retrieve a configuration file value. This will scan the loaded
        configuration files in order and return the first match.

        Args:
            *keys:
                The keys to the field. For example, to retrieve the value of
                "bar" under "foo", call get("foo", "bar"). Integers may also be
                used to index lists.

            default:
                The default value to return if no value was found.

        Returns:
            The target value, or the default if no value was found.
        """
        config = self.config
        origin = self._origin
        for i, key in enumerate(keys):
            try:
                config = config[key]
                try:
                    origin = origin[key]
                except TypeError:
                    pass
            except (KeyError, IndexError):
                return default
            except TypeError as err:
                paths = sorted(set(_nested_values(origin)))
                LOGGER.error(
                    "Failed to retrieve configuration value for %s: %s [%s]",
                    keys[: i + 1],
                    err,
                    ", ".join(shlex.quote(str(p)) for p in paths),
                )
                return default
        return config

    def _get_origin(self, *keys):
        """
        Similar to get() but returns the origin path for the given keys.
        """
        origin = self._origin
        if isinstance(origin, pathlib.Path):
            return origin
        for key in keys:
            origin = origin[key]
            if origin:
                return origin
        return None

    @property
    def gitlab(self):
        """
        The python-gitlab GitLab instance from the current configuration.
        """
        path = self.get("gitlab", "config")
        if path is None:
            LOGGER.warning("No python-gitlab configuration file specified.")
            path = os.getenv("PYTHON_GITLAB_CFG")
            if path is None:
                LOGGER.warning("PYTHON_GITLAB_CFG environment variable is unset.")
                return None
            path = pathlib.Path(path)
        else:
            origin_path = self._get_origin("gitlab", "config")
            if isinstance(origin_path, pathlib.Path):
                path = origin_path.resolve().parent.joinpath(path)
        path = path.resolve()
        section = self.get("gitlab", "section")
        if not section:
            LOGGER.warning(
                "No section specified for the python-gitlab configuration file: %s",
                path,
            )
        return gitlab.Gitlab.from_config(section, [str(path)])
