#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from typing import List


def read_lines(file_path: str) -> List[str]:
    """
    Return all file lines.
    """

    lines = []

    with open(file_path) as file:
        lines = file.readlines()

    return lines


def read_line(file_path: str) -> str:
    """
    Return 1st file line.
    """

    lines = read_lines(file_path)

    return lines[0].strip()


def read_version(base_path: str) -> str:
    """
    Return content of a "VERSION" file found at the "base_path".
    """

    version_file = os.path.join(base_path, "VERSION")

    return read_line(version_file)


def read_python_version(base_path: str) -> str:
    """
    Return content of a ".python-version" file found at the "base_path".
    """

    version_file = os.path.join(base_path, ".python-version")

    return read_line(version_file)
