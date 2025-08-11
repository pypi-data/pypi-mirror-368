#!/usr/bin/env python

"""
ideas from:

    https://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stderr-in-python/
    (archived as https://archive.is/0fNCo)

this version is much simplified since we redirect to /dev/null

"""

import os
import sys
from contextlib import contextmanager


@contextmanager
def suppress_stderr():
    original_stderr_fd = sys.__stderr__.fileno()
    sys.__stderr__.flush()

    # Save a copy of the original stderr fd in saved_stderr_fd
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        # Create a temporary file and redirect stderr to it
        fh = open(os.devnull, "wb")
        os.dup2(fh.fileno(), original_stderr_fd)

        yield

        # redirect back
        os.dup2(saved_stderr_fd, original_stderr_fd)
    finally:
        fh.close()
        os.close(saved_stderr_fd)
