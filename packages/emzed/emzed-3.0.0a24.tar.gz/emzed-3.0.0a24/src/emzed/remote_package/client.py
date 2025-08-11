#!/usr/bin/env python

import importlib
import signal
import traceback
from functools import partial
from multiprocessing.connection import Listener

from object_handling import ClientObjectMapper

signal.signal(signal.SIGINT, signal.SIG_IGN)

oo = ClientObjectMapper()
map_, register, unwrap, wrap = oo.map_, oo.register, oo.unwrap, oo.wrap


optimizations = {}


def main():
    commands = {
        "DELETE": delete_command,
        "SETITEM": setitem_command,
        "GETITEM": getitem_command,
        "GETATTR": getattr_command,
        "CALL": call_command,
        "ITER": iter_command,
        "NEXT": next_command,
        "DIR": dir_command,
        "INIT_OPTIMIZATIONS": init_optimizations_command,
    }

    KILLPILL = "KILLPILL"

    address = ("0.0.0.0", 0)

    with Listener(address, authkey=b"secret password") as listener:
        print("PORT=", listener.address[1], sep="")
        with listener.accept() as conn:
            while True:
                try:
                    command, args = conn.recv()
                except EOFError:
                    break
                if command == KILLPILL:
                    break
                if command == "IMPORT":
                    try:
                        module = importlib.import_module(args)
                        id_ = register(module)
                    except ImportError:
                        id_ = None
                    conn.send(id_)
                    continue
                args = unwrap(args)
                commands[command](conn, *args)


def init_optimizations_command(conn, path):
    global optimizations
    error = None
    try:
        module = {}
        exec(open(path).read(), module)
        optimizations.update(module["optimizations"])
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        error = e

    result = wrap(None)
    conn.send((error, result))


def delete_command(conn, id_):
    del map_[id_]


def call_command(conn, obj, args, kwargs):
    error = None
    result = None
    try:
        r = obj(*args, **kwargs)
        # handle pyopnms style "call by ref":
        result = (r, args)
    except Exception as e:
        error = e
        traceback.print_tb(e.__traceback__)

    result = wrap(result)
    conn.send((error, result))


def getattr_command(conn, obj, name):
    key = f"{obj.__class__.__name__}.{name}"
    if key in optimizations:
        result = optimizations[key]
        if not key.startswith("module."):
            result = partial(result, obj)
        conn.send((None, wrap(result)))
        return

    error = None
    result = None
    try:
        result = getattr(obj, name)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        error = e

    result = wrap(result)
    conn.send((error, result))


def dir_command(conn, obj):
    error = None
    result = None
    try:
        result = dir(obj)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        error = e

    result = wrap(result)
    conn.send((error, result))


def setitem_command(conn, obj, key, value):
    _call(conn, obj, "__setitem__", key, value)


def getitem_command(conn, obj, key):
    _call(conn, obj, "__getitem__", key)


def iter_command(conn, obj):
    _call(conn, obj, "__iter__")


def next_command(conn, obj):
    _call(conn, obj, "__next__")


def _call(conn, obj, method, *args, **kwargs):
    error = None
    result = None
    try:
        result = getattr(obj, method)(*args, **kwargs)
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        error = e.__class__(
            f"calling {obj}.{method} with args {args} {kwargs} failed: {e}"
        )

    result = wrap(result)
    conn.send((error, result))


if __name__ == "__main__":
    main()
