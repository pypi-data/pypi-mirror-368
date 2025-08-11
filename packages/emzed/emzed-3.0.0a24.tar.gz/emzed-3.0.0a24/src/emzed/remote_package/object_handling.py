#!/usr/bin/env python
import traceback
from pprint import pprint

import numpy as np

BASIC_TYPES = (int, float, str, bool, bytes, type(None))

OBJECT_PROXY = 1
ND_ARRAY = 2
PICKLED = 3


class ClientObjectMapper:
    def __init__(self):
        self.map_ = {}

    def register(self, data):
        id_ = id(data)
        if id_ not in self.map_:
            # print("REGISTER", hex(id_), data)
            self.map_[id_] = data
        return id_

    def get_registered(self, id_):
        try:
            return self.map_[id_]
        except KeyError:
            pprint({hex(id_): value for id_, value in self.map_.items()})
            raise

    def unwrap(self, data):
        try:
            type_, item = data
        except Exception:
            traceback.print_stack()
            raise
        if type_ is OBJECT_PROXY:
            return self.get_registered(item)

        if type_ is ND_ARRAY:
            bytes_, shape, dtype = item
            return np.ndarray(shape, dtype, bytes_)

        if isinstance(item, BASIC_TYPES):
            return item

        if isinstance(item, list):
            return [self.unwrap(ii) for ii in item]
        if isinstance(item, tuple):
            return tuple(self.unwrap(ii) for ii in item)
        if isinstance(item, set):
            return set(self.unwrap(ii) for ii in item)
        if isinstance(item, dict):
            return {self.unwrap(key): self.unwrap(value) for key, value in item.items()}

        if type_ == PICKLED:
            return item

        raise NotImplementedError(f"don't know how to unwrap {type(item)} {repr(item)}")

    def wrap(self, data):
        if isinstance(data, BASIC_TYPES):
            return 0, data

        if isinstance(data, list):
            return 0, [self.wrap(ii) for ii in data]
        if isinstance(data, tuple):
            return 0, tuple(self.wrap(ii) for ii in data)
        if isinstance(data, set):
            return 0, set(self.wrap(ii) for ii in data)
        if isinstance(data, dict):
            return 0, {self.wrap(key): self.wrap(value) for key, value in data.items()}

        if isinstance(data, np.ndarray):
            return ND_ARRAY, (data.tobytes(), data.shape, data.dtype.name)

        return OBJECT_PROXY, self.register(data)
