import os
import re
import msgpack
import feedparser
import tgcrypto
import boltons
import boltons.timeutils
import datetime
import environs
import sys
import subprocess
import threading
from . import loader, tools


def read(filename):
    try:
        with open(filename, 'rb') as fp:
            data = fp.read().decode('utf-8')
    except UnicodeDecodeError:
        with open(filename, 'r') as fp:
            data = fp.read()
    return data


def find_version(file_paths):
    if os.path.exists(file_paths):
        version_file = read(file_paths)
        version_match = re.search(
            r"^##\s(.*)$",
            version_file,
            re.M,
        )
        if version_match:
            return version_match.group(1)
        else:
            return None
    else:
        return None


__version__ = find_version(os.path.join(
    os.path.dirname(__file__), 'CHANGELOG.md'))
