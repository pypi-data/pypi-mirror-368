#!/usr/bin/env python

import os
import tempfile

import requests


def download(url):
    r = requests.get(url, allow_redirects=True)
    fd, path = tempfile.mkstemp()
    fh = os.fdopen(fd, "wb")
    fh.write(r.content)
    fh.close()
    return path
