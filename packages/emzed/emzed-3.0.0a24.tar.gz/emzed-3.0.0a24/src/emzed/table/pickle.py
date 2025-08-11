#!/usr/bin/env python

import dill


class Pickle:
    __slots__ = ["bytes"]

    def __init__(self, value):
        self.bytes = value

    def unpickle(self):
        return dill.loads(self.bytes)
