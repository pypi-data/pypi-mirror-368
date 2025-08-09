#!/usr/bin/env python
"""
Software Heritage functions.
"""

import logging
from urllib.parse import quote as urlquote

from ..requests import get_json_or_none

LOGGER = logging.getLogger(__name__)


def get_swhid_by_origin(origin):
    """
    Get a Software Heritage ID from an origin URL. This only includes the origin
    and repository ID.

    Args:
        origin:
            The origin URL of the software project.

    Returns:
        A Software Heritage ID string.
    """
    cache = get_swhid_by_origin.cache
    try:
        return cache[origin]
    except KeyError:
        pass

    url = f"https://archive.softwareheritage.org/api/1/origin/{origin}/get/"
    LOGGER.debug("Querying %s", url)
    # This is a bit kludgy with the empty tuple but it unifies the repeated
    # response checks.
    resp = url
    try:
        for keys in (
            (),
            ("origin_visits_url",),
            (0, "snapshot_url"),
            ("branches", "HEAD", "target_url"),
        ):
            for key in keys:
                resp = resp[key]
            resp = get_json_or_none(resp)
            if resp is None:
                return None
        swhid = f'swh:1:dir:{resp["directory"]};origin={urlquote(origin)}'
        cache[origin] = swhid
        return swhid
    except KeyError:
        return None


get_swhid_by_origin.cache = {}


def get_swh_url_by_origin(origin):
    """
    Get a Software Heritage link for an origin URL.

    Args:
        origin:
            The origin URL of the software project.

    Returns:
        A Software Heritage URL. The page may not exist.
    """
    return f"https://archive.softwareheritage.org/browse/origin/?origin_url={urlquote(origin)}"


def swh_project_exists(origin):
    """
    Check if the project exists on Software Heritage.

    Args:
        origin:
            The origin URL of the software project.

    Returns:
        True if the project exists, False otherwise.
    """
    return get_swhid_by_origin(origin) is not None
