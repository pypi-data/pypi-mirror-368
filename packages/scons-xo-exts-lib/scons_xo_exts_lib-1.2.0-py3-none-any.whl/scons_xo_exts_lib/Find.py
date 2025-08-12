#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from typing import List


def find_files(path: str) -> List[str]:
    if not os.path.exists(path):
        return []

    abs_path = os.path.abspath(path)
    files = os.listdir(abs_path)

    return list(map(lambda f: os.path.join(abs_path, f), files))


def find_last_directory(path: str) -> str:
    files = find_files(path)

    dirs = (d for d in files if os.path.isdir(d))
    dirs = sorted(dirs, reverse=True)

    if not dirs:
        raise RuntimeError("No files found and so also no latest directory")

    return dirs[0]
