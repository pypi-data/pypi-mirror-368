#!/usr/bin/env python3
"""
File operations.
"""

import filecmp
import logging
import pathlib
import shutil
import subprocess
import tempfile

from .common import ENCODING

LOGGER = logging.getLogger(__name__)


def diff(path_1, path_2, differ="vimdiff"):
    """
    Diff 2 paths.
    """
    if not path_2.exists():
        LOGGER.debug("Copying %s to %s", path_1, path_2)
        shutil.copy(path_1, path_2)
        return
    if not filecmp.cmp(path_1, path_2, shallow=False):
        #  if path_1.read_bytes().rstrip(b'\n') == path_2.read_bytes().rstrip(b'\n'):
        #      return
        cmd = [differ, str(path_1), str(path_2)]
        LOGGER.info("Diffing %s and %s", path_1, path_2)
        subprocess.run(cmd, check=True)


def update_content(content, path, encoding=ENCODING, **kwargs):
    """
    Interactively compare and merge new content. If the target path does not
    exist, the content will be written directly to it.

    Args:
        content:
            The new content to merge.

        path:
            The target path.

        encoding:
            The file encoding to use when writing the content. If None, the
            content is assumed to be bytes.

        **kwargs:
            Keyword arguments passed through to diff().
    """
    path = pathlib.Path(path).resolve()
    if not path.exists():
        LOGGER.debug("Writing content to %s", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if encoding is None:
            path.write_bytes(content)
        else:
            path.write_text(content, encoding=encoding)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = pathlib.Path(tmp_dir)
        tmp_path = tmp_dir / path.with_stem("new").name
        LOGGER.debug("Writing content to %s", tmp_path)
        if encoding is None:
            tmp_path.write_bytes(content)
        else:
            tmp_path.write_text(content, encoding=encoding)
        diff(tmp_path, path, **kwargs)
