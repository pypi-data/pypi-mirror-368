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


import os
import shutil
import subprocess
import sys
import time
import venv
import weakref
from multiprocessing.connection import Client
from threading import Thread

import numpy as np

here = os.path.dirname(os.path.abspath(__file__))

_map = {}

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def register(id_):
    obj = ObjectProxy(id_)
    _map[id_] = obj
    return obj


BASIC_TYPES = (int, float, str, bool, bytes, type(None))

OBJECT_PROXY = 1
ND_ARRAY = 2


def unwrap(data):
    type_, item = data

    if type_ is OBJECT_PROXY:
        id_ = item
        if id_ in _map:
            return _map[id_]
        return register(id_)

    if type_ is ND_ARRAY:
        bytes_, shape, dtype = item
        return np.ndarray(shape, dtype, bytes_)

    if isinstance(item, BASIC_TYPES):
        return item

    if isinstance(item, list):
        return [unwrap(ii) for ii in item]
    if isinstance(item, tuple):
        return tuple(unwrap(ii) for ii in item)
    if isinstance(item, set):
        return set(unwrap(ii) for ii in item)
    if isinstance(item, dict):
        return {unwrap(key): unwrap(value) for key, value in item.items()}

    raise NotImplementedError(f"don't know how to unwrap {item!r}")


def wrap(data):
    if isinstance(data, BASIC_TYPES):
        if getattr(data, "__module__", "").startswith("emzed."):
            raise ValueError("you must not pass emzed object to remote module.")
        return 0, data

    if isinstance(data, list):
        return 0, [wrap(ii) for ii in data]
    if isinstance(data, tuple):
        return 0, tuple(wrap(ii) for ii in data)
    if isinstance(data, set):
        return 0, set(wrap(ii) for ii in data)
    if isinstance(data, dict):
        return 0, {wrap(key): wrap(value) for key, value in data.items()}

    if isinstance(data, ObjectProxy):
        return OBJECT_PROXY, data.id_

    if isinstance(data, np.ndarray):
        return ND_ARRAY, (data.tobytes(), data.shape, data.dtype.name)

    raise NotImplementedError(f"dont know how to wrap {data!r}")


def python_exe_in(env_path):
    if sys.platform == "win32":
        python_venv_exe = os.path.join(env_path, "Scripts", "python.exe")
    else:
        python_venv_exe = os.path.join(env_path, "bin", "python")
    return python_venv_exe


def setup_remote_venv(env_path, packages):
    if sys.platform == "win32":
        python_venv_exe = python_exe_in(env_path)
        pip_exe = os.path.join(env_path, "Scripts", "pip.exe")
    else:
        python_venv_exe = python_exe_in(env_path)
        pip_exe = os.path.join(env_path, "bin", "pip")

    pip = f"{python_venv_exe} -m pip"

    if os.path.exists(pip_exe):

        def run(what, **kw):
            return subprocess.run(what, **kw)

        for name, version in packages:
            name = f'"{name}"'
            version = f'"{version}"'
            result = run(
                [
                    f"{python_venv_exe}",
                    "-c",
                    (
                        "import pkg_resources as p, packaging.version as v, sys;"
                        f"print({name}, p.require({name})[0].parsed_version._key[1]"
                        f", repr(v.parse({version})._key[1]));"
                        f"sys.exit(2 * int(p.require({name})[0].parsed_version._key[1]"
                        f" != v.parse({version})._key[1]))"
                    ),
                ],
                text=True,
                capture_output=True,
            )
            if result.returncode == 0:
                continue
            print("STDOUT")
            print(result.stdout)
            print("STDERR")
            print(result.stderr)
            print("---")

            msg = {1: "is not installed", 2: "has wrong version"}.get(result.returncode)
            print(f"rebuild venv: package {name} {msg}.")
            shutil.rmtree(env_path)
            break

    def pip_install(command):
        print(f"pip install {command}: ", end="", flush=True)
        result = subprocess.run(
            f"{pip} install {command}", capture_output=True, text=True, shell=True
        )
        if result.returncode == 0:
            print("✓", flush=True)
            return
        print("✗")
        print(result.stdout)
        print(result.stderr)
        raise OSError()

    # don't use else here!
    if not os.path.exists(pip_exe):
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        venv.create(env_path, with_pip=True)

        try:
            pip_install("-U pip setuptools packaging")
            for name, version in packages:
                pip_install(f"-U {name}=={version}")
        except Exception:
            try:
                pass
                # shutil.rmtree(env_path)
            except Exception:
                pass
            raise
    return python_venv_exe


class DirWrapper:
    def __init__(self, dir_):
        self.dir_ = dir_

    def __iter__(self):
        return iter(self.dir_)


BASIC_TYPES = (int, float, str, bool, bytes, type(None))

OBJECT_PROXY = 1
ND_ARRAY = 2


class ObjectMapper:
    def unwrap(self, data):
        type_, item = data

        if type_ is OBJECT_PROXY:
            id_ = item
            if id_ in self.map_:
                return self.map_[id_]
            return ObjectProxy(id_, self.map_, self.conn)

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

        raise NotImplementedError(f"don't know how to unwrap {item!r}")

    def wrap(self, data):
        if isinstance(data, BASIC_TYPES):
            if getattr(data, "__module__", "").startswith("emzed."):
                raise ValueError("you must not pass emzed object to remote module.")
            return 0, data

        if isinstance(data, list):
            return 0, [self.wrap(ii) for ii in data]
        if isinstance(data, tuple):
            return 0, tuple(self.wrap(ii) for ii in data)
        if isinstance(data, set):
            return 0, set(self.wrap(ii) for ii in data)
        if isinstance(data, dict):
            return 0, {self.wrap(key): self.wrap(value) for key, value in data.items()}

        if isinstance(data, ObjectProxy):
            return OBJECT_PROXY, data.id_

        if isinstance(data, np.ndarray):
            return ND_ARRAY, (data.tobytes(), data.shape, data.dtype.name)

        raise NotImplementedError(f"dont know how to wrap {data!r}")


class ObjectProxy(ObjectMapper):
    def __init__(self, id_, map_, conn):
        self.id_ = id_
        self.map_ = map_
        self.map_[id_] = self
        self.conn = conn
        kill_args = self.wrap((self.id_,))
        weakref.finalize(self, ObjectProxy._del_obj_callback, kill_args, self.conn)

    @staticmethod
    def _del_obj_callback(kill_args, conn):
        try:
            conn.send(("DELETE", kill_args))
        except IOError:
            # endpoint is already dead
            pass

    def _send(self, command, *args):
        args = self.wrap(args)
        self.conn.send((command, args))

    def _recv(self):
        while not self.conn.poll(timeout=0.001):
            pass
        error, result = self.conn.recv()
        if error:
            raise error
        return self.unwrap(result)

    def __dir__(self):
        self._send("DIR", self)
        return DirWrapper(self._recv())

    def __getstate__(self):
        raise NotImplementedError()

    def __setstate__(self, _):
        raise NotImplementedError()

    def __call__(self, *a, **kw):
        self._send("CALL", self, a, kw)
        result, a_after = self._recv()
        for a_i, a_after_i in zip(a, a_after):
            if isinstance(a_i, list):
                a_i[:] = a_after_i
        return result

    def __setitem__(self, key, value):
        self._send("SETITEM", self, key, value)
        return self._recv()

    def __getitem__(self, key):
        self._send("GETITEM", self, key)
        return self._recv()

    def __getattr__(self, name):
        self._send("GETATTR", self, name)
        return self._recv()

    def __iter__(self):
        self._send("ITER", self)
        iter_obj = self._recv()
        while True:
            self._send("NEXT", iter_obj)
            try:
                yield self._recv()
            except StopIteration:
                break


class RemoteModule(ObjectProxy):
    def __init__(self, python_venv_exe, module, env=None, conn=None):
        if conn is None:
            conn = start_remote_client(python_venv_exe, module, env or {})
        conn.send(("IMPORT", module))
        id_ = conn.recv()
        assert id_ is not None, f"loading {module} in remote interpreter failed"
        self._conn = conn
        super().__init__(id_, {}, conn)

    def load_optimizations(self, path):
        self._send("INIT_OPTIMIZATIONS", path)
        self._recv()

    def __spec__(self):
        return None

    @classmethod
    def deleted_callback(cls, conn, proc):
        try:
            cls._send("KILLPILL")
        except IOError:
            # endpoint is already dead
            pass
        try:
            proc.terminate()
        except IOError:
            # endpoint is already dead
            pass


class DelayedRemoteModule:
    def __init__(self, python_venv_exe, module, env=None, conn=None):
        self._python_venv_exe = python_venv_exe
        self._module = module
        self._env = env
        self._conn = conn

    def load_optimizations(self, path):
        self._path = path

    def __spec__(self):
        return None

    def __dir__(self):
        self._load_delayed()
        return dir(self)

    def __getattr__(self, name):
        self._load_delayed()
        return getattr(self, name)

    def _load_delayed(self):
        rm = RemoteModule(self._python_venv_exe, self._module, self._env, self._conn)
        rm.load_optimizations(self._path)
        self.__class__ = rm.__class__
        self.__dict__ = rm.__dict__


def start_remote_client(python_venv_exe, module_name, env_updates):
    port = None
    proc = None

    env = dict(os.environ)
    env.update(env_updates)

    def start_listener():
        nonlocal port, proc
        with subprocess.Popen(
            [python_venv_exe, "-u", f"{os.path.join(here, 'client.py')}", module_name],
            stdout=subprocess.PIPE,
            text=True,
            env=env,
        ) as proc:
            for line in iter(proc.stdout.readline, ""):
                line = line.rstrip()
                if line.startswith("PORT="):
                    _, _, port = line.partition("=")
                    print(f"{module_name} client started.")
                    continue
                print(f"{module_name}: {line}", flush=True)

    t = Thread(target=start_listener)
    t.daemon = True
    t.start()

    while True:
        if port is None:
            time.sleep(0.1)
            continue
        try:
            conn = Client(("127.0.0.1", int(port)), authkey=b"secret password")
            break
        except ConnectionRefusedError:
            time.sleep(0.1)
            continue
    print(f"connected to {module_name} client.")
    return conn
