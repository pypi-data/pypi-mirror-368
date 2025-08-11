#!/usr/bin/env python

import os
import tempfile
from contextlib import contextmanager


@contextmanager
def temp_file_path():
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "tempfile")
    try:
        yield path
    finally:
        try:
            os.remove(path)
        except IOError:
            pass
        try:
            os.rmdir(folder)
        except IOError:
            pass
