#!/usr/bin/env python3
"""
Utility functions.
"""

import logging
import re
import textwrap

LOGGER = logging.getLogger(__name__)


def choose(items, include_none=False):
    """
    Prompt the user to choose an item from an iterable of items.

    Args:
        items:
            The iterable of items.

        include_none:
            If True, allow the user to choose None even if it is not in the
            list.

    Returns:
        The chosen item.
    """
    items = sorted(items)
    if include_none and None not in items:
        items.append(None)
    if not items:
        LOGGER.warning("No items to choose.")
        return None
    n_items = len(items)
    if n_items == 1:
        return items[0]
    while True:
        print("Choose one of the following:")
        for i, item in enumerate(items, start=1):
            print(f"{i:d} {item}")
        choice = input(f"Enter an integer in the range 1-{n_items:d} and press enter. ")
        try:
            choice = int(choice)
        except ValueError:
            LOGGER.error('"%s" is not a valid integer.', choice)
            continue
        if choice < 1 or choice > n_items:
            LOGGER.error("Invalid choice.")
            continue
        return items[choice - 1]


def join_docstrings(delimiter, docstrings):
    """
    Join docstrings with a delimiter. The indentation of the last docstring is
    preserved for the joined docstring.

    Args:
        delimiter:
            The delimiter to place between the docstrings. If None, no delimiter
            is emitted.

        docstrings:
            A list of docstrings.

    Returns:
        The docstring that results from joining the docstrings.
    """
    docstrings = list(docstrings)
    if not docstrings:
        LOGGER.warning("No docstrings passed to join_docstrings.")
        return None
    if len(docstrings) == 1:
        return docstrings[0]

    regex = re.compile("^( *)")
    indent = None
    for line in docstrings[-1].splitlines():
        line = line.rstrip()
        if not line:
            continue
        match = regex.match(line)
        if indent is None or len(match.group(1)) < len(indent):
            indent = match.group(1)

    docstrings = (textwrap.dedent(d).strip("\n") for d in docstrings)
    delimiter = f"\n\n{delimiter}\n\n" if delimiter else "\n\n"
    result = delimiter.join(docstrings)
    return textwrap.indent(result, indent)


def prepend_docstrings(delimiter, *objects):
    """
    Decorator to prepend docstrings to an object's docstring.

    Args:
        delimiter:
            The delimiter to pass to join_docstrings.

        objects:
            The objects from which to retrieve the docstrings.
    """

    def _decorator(obj):
        docstrings = (o.__doc__ for o in objects)
        obj.__doc__ = join_docstrings(delimiter, (*docstrings, obj.__doc__))
        return obj

    return _decorator


def format_docstring_for_cell(docstring):
    """
    Format a docstring for a table cell. This just dedents the block, replaces
    newlines and handles reStructuredText links. At the time of writting, none
    of the proposed packages for converting docstrings to Markdown worked
    reliably.

    Args:
        docstring:
            The docstring.

    Returns:
        The docstring content as a single-line Markdown string that may contain
        ``<br />`` tags.

    TODO:
        Replace this with a reliable function to convert a docstring to either
        Markdown or HTML.
    """
    content = []
    links = {}
    link_prefix = ".. _"
    link_prefix_len = len(link_prefix)
    for line in docstring.splitlines():
        line = line.rstrip()
        sline = line.lstrip()
        if sline.startswith(link_prefix):
            name, url = sline[link_prefix_len:].split(": ", 1)
            links[name] = url
        else:
            content.append(line)
    content = "\n".join(content)
    for name, url in links.items():
        content = content.replace(f"`{name}`_", f"[{name}]({url})")
    content = content.replace("``", "`").rstrip()
    content = textwrap.dedent(content).strip()
    content = re.sub("\n\n+", "\n\n", content)
    return content.replace("\n\n", "<br />").replace("\n", " ")
