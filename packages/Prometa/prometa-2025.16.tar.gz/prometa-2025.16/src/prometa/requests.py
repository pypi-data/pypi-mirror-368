#!/usr/bin/env python
"""
Convenience functions for the requests package.
"""


import logging

import requests

LOGGER = logging.getLogger(__name__)


def get_json_or_none(url, timeout=5):
    """
    Request a URL and return either the JSON response or None if the request
    failed. An error message will be logged in the latter case.

    Args:
        url:
            The URL to request. It should return a JSON response.

    Returns:
        The parsed JSON object, or None if the request failed.
    """
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as err:
        LOGGER.error("Failed to retrieve %s: %s", url, err)
        return None
