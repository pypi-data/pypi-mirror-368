#!/usr/bin/env python
"""
HAL open science functions.

https://api.archives-ouvertes.fr/docs/search
"""

import logging
from urllib.parse import quote as urlquote

from ..requests import get_json_or_none

LOGGER = logging.getLogger(__name__)


def get_hal_url_by_origin(origin):
    """
    Get the HAL ID by origin.
    """
    cache = get_hal_url_by_origin.cache
    try:
        return cache[origin]
    except KeyError:
        pass

    query = origin.split("://", 1)[1]
    search_url = f"https://api.archives-ouvertes.fr/search/?q={urlquote(query)}"
    LOGGER.debug("Querying %s", search_url)
    resp = get_json_or_none(search_url)
    if resp is None:
        return None
    for doc in resp["response"]["docs"]:
        label = doc["label_s"]
        if f"origin={origin};" in label:
            url = doc["uri_s"]
            cache[origin] = url
            return url
    return None


get_hal_url_by_origin.cache = {}


def get_hal_id_from_url(url):
    """
    Extract the HAL ID from a HAL URL.
    """
    return url.rsplit("/", 1)[1]
