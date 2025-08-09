#!/usr/bin/env python
"""
All things specific to Python (pyproject.toml, PyPI, etc.)
"""

import difflib
import logging
from urllib.parse import quote as urlquote

from spdx_license_list import LICENSES as SPDX_LICENSES
from trove_classifiers import classifiers as py_classifiers

from ..requests import get_json_or_none

LOGGER = logging.getLogger(__name__)


def get_pypi_url(name):
    """
    Get the URL to the project's page on PyPI if it exists.

    Args:
        name:
            The project name.

    Returns:
        The project URL, or None if it does not exist.
    """
    url = f"https://pypi.org/pypi/{urlquote(name)}/json"
    LOGGER.debug("Querying %s", url)
    resp = get_json_or_none(url)
    if resp is None:
        return None
    try:
        return resp["info"]["package_url"]
    except KeyError:
        return None


def get_license_classifier(spdx_id):
    """
    Get the Python license classifier for the given SPDX license ID.

    Args:
        spdx_id:
            The SPXD license ID.

    Returns:
        The corresponding Python trove classifier if found, else None.
    """
    spdx_data = SPDX_LICENSES.get(spdx_id)
    if not spdx_data:
        LOGGER.warning("%s is not a recognized SPDX license ID.", spdx_id)
        return None
    name = spdx_data.name
    if spdx_data.osi_approved:
        expected = f"License :: OSI Approved :: {name}"
    else:
        expected = "License :: {name}"
    if expected in py_classifiers:
        return expected
    closest = difflib.get_close_matches(expected, py_classifiers)
    if not closest:
        LOGGER.warning(
            "Failed to map SPDX license ID %s to a Python trove classifier.", spdx_id
        )
        return None
    return closest[0]
