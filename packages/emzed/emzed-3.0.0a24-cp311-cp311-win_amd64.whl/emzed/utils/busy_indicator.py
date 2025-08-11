# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import itertools
import sys
import threading
import time
from contextlib import contextmanager


def _zig_zag(i, n):
    i = i % (2 * n - 2)
    if i >= n:
        i = 2 * n - 2 - i
    return i


def _print_progress(i, n, started, prefix):
    pos = _zig_zag(i, n + 1)
    elements = ["|"] * pos + (n - pos) * [" "]
    bar = "[" + "".join(elements) + "]"
    tp = time.time() - started

    print("\r" + prefix + _format_time(tp) + " " + bar, end="")


def _format_time(t):
    if t is None:
        return "??:??:??.?"
    minutes, seconds = divmod(t, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:02.0f}:{:02.0f}:{:04.1f}".format(hours, minutes, seconds)


class _BusyPrinter(threading.Thread):
    def __init__(self, name, n, dt):
        super().__init__()
        self._name = name
        self._n = n
        self._dt = dt
        self._running = True

    def run(self):
        prefix = self._name + ": "

        started = time.time()
        for i in itertools.count():
            if not self._running:
                break
            _print_progress(i, self._n, started, prefix)
            sys.stdout.flush()
            time.sleep(self._dt)
        print(
            "\r"
            + prefix
            + _format_time(time.time() - started)
            + " total runtime"
            + " " * (self._n + 3 - 13)
        )
        sys.stdout.flush()


@contextmanager
def busy_indicator(name, n=15, dt=0.07):
    t = _BusyPrinter(name, n, dt)
    t.start()
    try:
        yield
    finally:
        t._running = False
        t.join()
