#!/usr/bin/env python
"""Package stub."""

import importlib

from .host import GitHost
from .repo import GitRepo

# Convert to a loop later if other hosts are added.
importlib.import_module(".gitlab.host", __name__)

__all__ = ["GitHost", "GitRepo"]
