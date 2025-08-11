#!/usr/bin/env python

import os
import sys
from multiprocessing import current_process

import numpy as np

# from emzed.config import folders
from emzed.remote_package import (
    DelayedRemoteModule,
    RemoteModule,
    python_exe_in,
    setup_remote_venv,
)

from .stderr_redirector import suppress_stderr

if "pyopenms" not in sys.modules:
    env_path = os.path.join(sys.prefix, "share", "pyopenms_venv")

    PYOPENMS_VERSION = "3.3.0"

    is_main_process = current_process().name == "MainProcess"

    if is_main_process:
        print("start remote ip in", env_path)
        python_venv_exe = setup_remote_venv(
            env_path,
            [
                ("pyopenms", PYOPENMS_VERSION),
                ("numpy", str(np.__version__)),
            ],
        )
    else:
        python_venv_exe = python_exe_in(env_path)

    Module = RemoteModule if is_main_process else DelayedRemoteModule

    with suppress_stderr():
        pyopenms = sys.modules["pyopenms"] = Module(python_venv_exe, "pyopenms")
        here = os.path.dirname(os.path.abspath(__file__))
        pyopenms.load_optimizations(os.path.join(here, "optimizations.py"))

else:
    print("skip start remote pyopenms.")


def encode(s):
    if isinstance(s, str):
        return s.encode("utf-8")
    return s


def decode(s):
    if isinstance(s, bytes):
        return str(s, "utf-8")
    return s
