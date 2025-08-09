#!/usr/bin/env python3
"""
Insert data into the README.
"""

import functools
import logging
import shlex
import subprocess

from .exception import PrometaException
from .id.hal import get_hal_url_by_origin
from .id.swh import get_swh_url_by_origin, swh_project_exists
from .insert import MarkdownInserter

LOGGER = logging.getLogger(__name__)


# Each recognized label is defined in a method named process_label_<label> where
# <label> is the recognized label. These methods must follow a specific
# docstring format as they are used to document the supported labels
# automatically in Prometa's README.
#
# The format follows the standard documentation format with a brief description,
# Args, Returns, Raises, etc. The docstring must end with the following format:
#
#     <standard docstring ends here>
#
#     .. code-block:: markdown
#         :dedent:
#
#         `<label> [<arg1> <arg2> ...]`
#
#         <Markdown description of the label and its eventual arguments.


class ReadmeInserter(MarkdownInserter):
    """
    Processes several labels to insert various content in the README file.
    """

    def __init__(self, project):
        super().__init__()
        self.project = project

    @functools.cached_property
    def labels(self):
        """
        The dict mapping labels to their methods.
        """
        labels = {}
        prefix = "process_label_"
        prefix_len = len(prefix)
        for attr in dir(self):
            if attr.startswith(prefix):
                labels[attr[prefix_len:]] = getattr(self, attr)
        return labels

    @staticmethod
    def _split_level(label):
        """
        Extract the header level from a label.

        Args:
            label:
                A string with the label and header leavel in format "<label>
                <level>".

        Returns:
            The label and the level. If no level was found, the level defaults
            to 1.
        """
        label = label.strip()
        try:
            label, level = label.split(None, 1)
        except ValueError:
            LOGGER.debug("Missing header level in label [%s]: assuming 1", label)
            return label, 1
        return label, int(level)

    @staticmethod
    def _get_lang_and_command(label):
        """
        Extract command and optional language from the label.

        Args:
            label:
                A string of the format "command[:<lang>] <cmd>", e.g. "command
                echo test" or "command:yaml some_cmd_to_print_yaml". The command
                string will be parsed by shlex.split().

        Returns:
            The language and the command. The language will be None if not found
            and the command will be a list of command words.
        """
        label, command = label.split(None, 1)
        try:
            label, lang = label.split(":", 1)
            lang = lang.strip()
        except ValueError:
            lang = None
        return lang, shlex.split(command)

    def process_label_verbatim(self, label, content):  # pylint: disable=unused-argument
        """
        Do nothing.

        Args:
            label:
                The insert label (see below).

            content:
                The current block content.

        Returns:
            False

        .. code-block:: markdown
            :dedent:

            `verbatim`

            Return the content between the invisible comments as-is. This no-op
            label can be used to wrap examples of other labels and anything else
            that should not be modified.
        """
        return content

    def process_label_citation(
        self, label, _content
    ):  # pylint: disable=unused-argument
        """
        Get the section containing citation examples for different targets.

        Args:
            label:
                The insert label (see below).

            _content:
                The current block content.

        Returns:
            A Markdown string containing the citations section.

        .. code-block:: markdown
            :dedent:

            `citations <level>`

            Convert CITATIONS.cff to different formats using with
            [cffconvert](https://pypi.org/project/cffconvert/) and insert them
            into the README.

            The `<level>` parameter is an integer to indicate the heading level
            of the current context. It will be used to insert nested headers in
            the content. If omitted, level 1 is assumed.
        """
        path = self.project.citation_cff_path
        citation_cff_url = self.project.git_repo.get_main_blob_url(path.name)
        blocks = [
            "Please cite this software using the metadata provided in "
            f"[{path.name}]({citation_cff_url}). "
            "The following extracts are provided for different applications.",
            "",
        ]
        if path.exists():
            for fmt in (
                "cff",
                "apalike",
                "bibtex",
                "endnote",
                "ris",
                "schema.org",
                "zenodo",
            ):
                cmd = ["cffconvert", "-i", str(path), "-f", fmt]
                LOGGER.debug("Converting %s to %s", path, fmt)
                output = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                ).stdout.decode()
                blocks.append(f"{fmt}\n: ~~~\n{output.strip()}\n~~~\n")
        else:
            LOGGER.error("Failed to insert citations: %s does not exist.", path)
            blocks.append(f"**ERROR**: {path.name} does not exist!")
        return "\n".join(blocks)

    def process_label_links(self, label, _content):
        """
        Get the section containing standard links.

        Args:
            label:
                The insert label (see below).

            _content:
                The current block content.

        Returns:
            A Markdown string containing the links section.

        .. code-block:: markdown
            :dedent:

            `links <level>`

            Insert project links such as homepage, source code repository, issue
            tracker, documentation, etc. Optional third-part repository links
            (PyPI, SWH, HAL) will also be inserted if Prometa detects that they
            contain the project.

            The `<level>` parameter is an integer to indicate the heading level
            of the current context. It will be used to insert nested headers in
            the content. If omitted, level 1 is assumed.
        """
        label, level = self._split_level(label)
        header_prefix = "#" * (level + 1)

        lines = [f"{header_prefix} GitLab", ""]

        lines.extend(
            self.get_link(name.title(), link)
            for name, link in self.project.urls.items()
        )

        other_repos = []
        if any(self.project.packages):
            lines.append(
                self.get_link(
                    "GitLab package registry",
                    self.project.git_repo.get_section_url("packages"),
                )
            )
            for pkg in self.project.packages.values():
                for name, url in pkg.links:
                    other_repos.append(self.get_link(name, url))

        origin_url = self.project.git_repo.public_git_url
        if swh_project_exists(origin_url):
            other_repos.append(
                self.get_link("Software Heritage", get_swh_url_by_origin(origin_url))
            )

        hal_url = get_hal_url_by_origin(origin_url)
        if hal_url:
            other_repos.append(self.get_link("HAL open science", hal_url))

        if other_repos:
            lines.extend(("", f"{header_prefix} Other Repositories", "", *other_repos))

        return "\n".join(
            line if not line or line.startswith("#") else f"* {line}" for line in lines
        )

    def process_label_command(self, label, _content):
        """
        Get the output of a command.

        Args:
            label:
                The insert label (see below).

            _content:
                The current block content.

        Returns:
            A Markdown string containing the command output (see below for
            details about how to control the wrapping codeblock). If the user
            declines the command when prompted, None is returned instead.

        Raises:
            PrometaException:
                A CalledProcessError or OSError occurred when running the
                command.

        .. code-block:: markdown
            :dedent:

            `command_output[:<lang>] <command string>`

            Insert the output of an arbitrary command. The user will be prompted
            to confirm the command before it is run to prevent unknowingly
            executing arbitrary code, unless Prometa is currently configured to
            trust all commands (e.g. via the `--trust` command-line option).

            `<command string>` should be a valid shell command string. It will
            be interpreted internally using
            [shlex.split()](https://docs.python.org/3/library/shlex.html#shlex.split).
            The confirmation prompt will show the user the parsed command.

            The output will be wrapped in a code block. The user may specify an
            optional language for syntax highlighting by appending `:<lang>` to
            the end of the `command_output` label, where `<lang>` is the desired
            language. For example, to insert YAML output, use
            `command_output:yaml command arg1 arg2 ...`.

            The command also supports the custom language tag
            "embedded_markdown", which will insert the command's output into the
            Markdown document directly instead of fencing it in a code block.
        """
        lang, command = self._get_lang_and_command(label)
        if not self.project.config.get("trust_commands", default=False):
            ans = input(f"Run command {command}? [y/N] ")
            if ans.strip().lower() != "y":
                LOGGER.info("Skipping command %s", command)
                return None
        LOGGER.info("Running command: %s", command)
        try:
            output = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                cwd=self.project.readme_md_path.parent,
            ).stdout.decode()
        except (subprocess.CalledProcessError, OSError) as err:
            raise PrometaException(err) from err
        if lang == "embedded_markdown":
            return output
        lang = lang if lang else ""
        return f"~~~{lang}\n{output}\n~~~\n"

    def process_label_badges(self, label, _content):
        """
        Insert badges into the README.

        Args:
            label:
                The insert label (see below).

            _content:
                The current block content.

        Returns:
            A Markdown string containing badges for the README.

        Raises:
            PrometaException:
                A remote API call failed.

        .. code-block:: markdown
            :dedent:

            `badges <api> [<api> ...]`

            Insert all badges currently configured on the project's Git host.
            `<api>` specifies the API to use to query the badges. Currently only
            the following value is supported.

            gitlab
            : Insert all badges from the project's remote GitLab instance
            origin.  The badges are retrieved via calls to the GitLab API so
            this requires the "gitlab" section to be configured in the project's
            configuration file (see the configuration section for details).
        """
        badges = []
        apis = label.split()[1:]
        for api in apis:
            if api == "gitlab":
                if self.project.git_host:
                    with self.project.git_host.gitlab_api as api:
                        badges.extend(api.get_markdown_badges())
                else:
                    LOGGER.warning(
                        "Failed to retrieve badges from GitLab API: "
                        "no GitLab host configured for project"
                    )
            else:
                LOGGER.warning("Ignoring unrecognized badge API: %s", api)
        if badges:
            return " ".join(badges)
        return None

    def get_output(self, label, content):
        """
        Override parent get_output.
        """
        LOGGER.debug("Processing label %s", label)
        for key, method in self.labels.items():
            if label.startswith(key):
                result = method(label, content)
                if result is None:
                    LOGGER.warning(
                        'Label "%s" produced no content. Re-inserting original content.',
                        label,
                    )
                    return None
                return result
        LOGGER.warning("Unhandled label in README: %s", label)
        return content
