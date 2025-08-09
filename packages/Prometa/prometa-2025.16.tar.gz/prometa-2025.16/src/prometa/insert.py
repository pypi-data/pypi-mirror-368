#!/usr/bin/env python3
"""
Base class for inserting content into text files.
"""

import pathlib
import re

from .common import ENCODING
from .file import update_content


class Inserter:
    """
    Insert updated content into a text file.
    """

    def __init__(self, regex):
        """
        Args:
            regex:
                A compiled regular expression.
        """
        self.regex = regex

    def insert(self, match):
        """
        Given a regular expression match, return the content to insert.

        Args:
            match:
                The Match object.

        Returns:
            The string to substitute for the match.
        """
        return match.group(0)

    def update(self, path, encoding=ENCODING):
        """
        Insert the configured content into the file.
        """
        text = pathlib.Path(path).resolve().read_text(encoding=encoding)
        text = self.regex.sub(self.insert, text)
        update_content(text, path)


class MarkdownInserter(Inserter):
    """
    Inserter with custom regex for invisible comments in Markdown files.

    In Markdown, a link label for a simple hash results in no output for most
    common Markdown processors: "[comment]: #". Note that these must be
    proceeded by blank lines to be recognized in Markdown.

    This class recognized blocks that begin with a comment prefixed with
    "insert: " and end with a comment containing only "/insert". Both comments
    must have the same indentation level and the inserted text will be indented
    to the same level.
    """

    def __init__(self):
        regex = re.compile(
            r"^(?P<indent>[ \t]*)\[insert: (?P<label>.+?)\]: #\n"
            r"(?:(?P<content>.*?)\n)?"
            r"^(?P=indent)\[/insert: (?P=label)]: #\n",
            re.MULTILINE | re.DOTALL,
        )
        super().__init__(regex)

    @staticmethod
    def get_link(label, url):
        """
        Get the Markdown link.

        Args:
            label:
                The label shown for the link.

            url:
                The URL of the link.

        Return:
            The Markdown link as a string.
        """
        return f"[{label}]({url})"

    def get_output(self, label, content):  # pylint: disable=unused-argument
        """
        Get output to replace the given label. Override this to insert custom
        content.

        Args:
            label:
                The label in the comment pair that was matched.

            content:
                The content between the matched comments.

        Returns:
            The content to insert, or None if the label was not recognized.
        """
        return None

    def insert(self, match):
        indent = match["indent"]
        label = match["label"].strip()
        content = match["content"]
        output = self.get_output(label, content)  # pylint: disable=assignment-from-none
        if output is None:
            return match.group(0)
        output = "\n".join(f"{indent}{line}" for line in output.strip("\n").split("\n"))
        return f"{indent}[insert: {label}]: #\n\n{output}\n\n{indent}[/insert: {label}]: #\n"
