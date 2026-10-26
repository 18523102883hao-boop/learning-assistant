"""The adult command-line JSON protocol always uses UTF-8, including on Windows."""

import sys


def configure_utf8_stdio():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
