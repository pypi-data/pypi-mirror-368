#!/usr/bin/env python

import itertools
from collections import defaultdict

import numpy as np


class NeighbourSearch:
    def __init__(self, data, tolerances):
        assert isinstance(data, np.ndarray)
        assert isinstance(tolerances, np.ndarray)
        assert data.ndim == 2
        assert tolerances.ndim == 1
        assert data.shape[1] == tolerances.shape[0]
        self._data = data
        self._bin_widths = tolerances

        self._setup_data_structures()

    def find_matches(self, index, row):
        bin_ = self._compute_bin(row)

        row = np.atleast_2d(row)
        assert row.ndim == 2
        assert row.shape[1] == self._data.shape[1]

        candidates = dict()

        for neigbour_bin in self._walk_neighbours(bin_):
            for i, entry in self._bins[neigbour_bin]:
                if i in candidates:
                    continue
                candidates[i] = entry

        for i, entry in candidates.items():
            if i == index:
                continue
            if np.all(np.abs(entry - row) < self._bin_widths):
                yield i

    def _setup_data_structures(self):
        self._setup_neighbours()
        self._fill_bins()

    def _fill_bins(self):
        self._bins = defaultdict(list)

        compute_bin = self._compute_bin
        walk_neighbours = self._walk_neighbours

        for index, row in enumerate(self._data):
            central_bin = compute_bin(row)
            for bin_ in walk_neighbours(central_bin):
                self._bins[bin_].append((index, row))

    def _compute_bin(self, row):
        return (row / self._bin_widths).astype(int)

    def _setup_neighbours(self):
        n = self._data.shape[1]
        single_offset = np.array([-1, 0, 1])
        self._offsets = list(itertools.product(*(single_offset,) * n))

    def _walk_neighbours(self, central_bin):
        for offset in self._offsets:
            yield tuple(central_bin + offset)
