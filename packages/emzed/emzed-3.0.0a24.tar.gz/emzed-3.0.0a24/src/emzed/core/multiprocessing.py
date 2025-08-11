#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

import concurrent.futures
import multiprocessing as _m
import queue
import sys
from contextlib import contextmanager
from functools import wraps
from threading import Thread


def initializer(stderr, stdout):
    sys.stderr = stderr
    sys.stdout = stdout


class Multiprocessing:
    def __getattr__(self, name):
        return getattr(_m, name)

    @contextmanager
    def Pool(self, n):
        m = _m.Manager()
        stdout_to_queue, thread_out = setup(sys.stdout, m)
        stderr_to_queue, thread_err = setup(sys.stderr, m)
        thread_out.start()
        thread_err.start()

        stored_e = None

        with concurrent.futures.ProcessPoolExecutor(
            n,
            mp_context=_m.get_context("spawn"),
            initializer=initializer,
            initargs=(stdout_to_queue, stderr_to_queue),
        ) as p:
            try:
                yield p
            except Exception as e:
                stored_e = e

        thread_out.running = False
        thread_err.running = False
        thread_out.join()
        thread_err.join()

        if stored_e is not None:
            raise stored_e


def setup(stream, m):
    q = m.Queue()
    return StreamToQueue(q), ReadFromQueueAndPrint(q, stream)


class StreamToQueue:
    def __init__(self, queue):
        self.queue = queue

    def write(self, what):
        self.queue.put(what)

    def flush(self):
        pass


class ReadFromQueueAndPrint(Thread):
    def __init__(self, queue, stream):
        super().__init__()
        self.queue = queue
        self.stream = stream
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                msg = self.queue.get(block=True, timeout=0.01)
                self.stream.write(msg)
                self.stream.flush()
            except queue.Empty:
                pass


def inject_streams(stdout_to_queue, stderr_to_queue, function):
    @wraps(function)
    def wrapped(*a, **kw):
        before_out = sys.stdout
        before_err = sys.stderr

        sys.stdout = stdout_to_queue
        sys.stderr = stderr_to_queue
        try:
            return function(*a, **kw)
        finally:
            sys.stdout = before_out
            sys.stderr = before_err

    return wrapped


multiprocessing = Multiprocessing()
