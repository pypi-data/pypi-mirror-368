#!/usr/bin/env python
# the module "subprocess" requires Python 2.4

import sys
import time
import traceback

if True:  # avoids resortin by Isort
    # patch Popen to be unbuffered again (changed in Python 3.3):
    import subprocess

    orig = subprocess.Popen

    def _Popen(*a, **kw):
        kw["bufsize"] = 0
        return orig(*a, **kw)

    subprocess.Popen = _Popen

    # inject python 2 artefact:
    __builtins__["NoneType"] = type(None)
    import pyper
    from pyper import RError  # noqa: F401
    from pyper import R, _mystr


# patch module global function:


def seqstr(obj, orig=pyper.SeqStr):
    if len(obj) == 0:
        return "list()"
    return orig(obj)


pyper.SeqStr = seqstr


def sendAll(p, s, orig=pyper.sendAll):
    # fixes issues with unbuffered response from R
    # p.stdin.write(b"flush.console();")
    rv = orig(p, s)
    # p.stdin.write(b"flush.console();")
    # p.stdin.flush()
    return rv


# pyper.sendAll = sendAll


def _readLine(p, **b):
    rv = _mystr(p.stdout.readline())
    if rv[0] not in ">[":
        sys.stdout.write(rv)
        sys.stdout.flush()
    return rv


pyper.readLine = _readLine


pyper.str_func[list] = seqstr
pyper.str_func[tuple] = seqstr


def on_die(prog, newline):
    try:
        if prog:
            print("send q() command")
            sendAll(prog, 'q("no")' + newline)
            time.sleep(0.5)
            prog.terminate()
            prog.poll()
            print("R interpreter shut down")
    except Exception:
        traceback.print_exc()


class PatchedR(R):
    def __init__(
        self,
        RCMD="R",
        max_len=1000,
        use_numpy=True,
        use_pandas=True,
        use_dict=None,
        host="localhost",
        user=None,
        ssh="ssh",
        return_err=True,
    ):
        super().__init__(
            RCMD, max_len, use_numpy, use_pandas, use_dict, host, user, ssh, return_err
        )
        self.install_del_callaback()
