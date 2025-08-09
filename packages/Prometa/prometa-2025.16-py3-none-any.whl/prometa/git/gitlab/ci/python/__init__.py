#!/usr/bin/env python
"""Package stub."""

import importlib
import logging

LOGGER = logging.getLogger(__name__)


# Import modules to ensure that subclasses are registered.
for pkg in ("register_python_package", "pylint"):
    LOGGER.debug("Importing %s.%s", __name__, pkg)
    importlib.import_module(f".{pkg}", __name__)
