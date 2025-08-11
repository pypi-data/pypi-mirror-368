#!/usr/bin/env python

from functools import wraps

import numpy as np


def ignore_overflow(func):
    @wraps(func)
    def wrapped(*a, **kw):
        try:
            before = np.seterr(over="ignore")
            return func(*a, **kw)
        finally:
            np.seterr(**before)

    return wrapped
