#!/usr/bin/env python3
"""\
Print documentation of all recognized README insert labels.\
"""

import logging
import sys
import textwrap

from ..readme import ReadmeInserter

LOGGER = logging.getLogger(__name__)


def document_labels():
    """
    Document recognized README labels. The documentation is printed to STDOUT in
    Markdown.
    """
    level = 1
    try:
        level = int(sys.argv[1])
    except IndexError:
        pass
    except ValueError:
        LOGGER.error("Failed to interpret header level: %s")
    header_prefix = "#" * level

    inserter = ReadmeInserter(None)
    for _name, method in sorted(inserter.labels.items()):
        lines = method.__doc__.splitlines()
        index = lines.index(".. code-block:: markdown") + 1
        while lines[index].strip():
            index += 1
        index += 1
        label = lines[index].strip(" `")
        first_word = label.split(None, 1)[0]
        if ":" in first_word:
            first_word = first_word.split(":", 1)[0]
        markdown = "\n".join(lines[index + 2 :])
        markdown = textwrap.dedent(markdown)
        print(
            f"""{header_prefix} {first_word}

~~~
[insert: {label}]: #

<content>

[/insert: {label}]: #
~~~

{markdown}

"""
        )
