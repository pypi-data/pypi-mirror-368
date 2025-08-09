#!/usr/bin/env python
"""Package stub."""

import importlib
import logging

LOGGER = logging.getLogger(__name__)


# Import modules to ensure that subclasses are registered.
for pkg in ("black", "hatch", "isort", "pylint", "pypi", "pypi_downloads"):
    LOGGER.debug("Importing %s.%s", __name__, pkg)
    importlib.import_module(f".{pkg}", __name__)
