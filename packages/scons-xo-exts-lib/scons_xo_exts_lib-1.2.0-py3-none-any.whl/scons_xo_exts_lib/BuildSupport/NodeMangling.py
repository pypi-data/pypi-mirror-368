#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import re


def get_first_node(nodes):
    if isinstance(nodes, list):
        return nodes[0]

    return nodes


def get_first_directory(nodes):
    node = get_first_node(nodes=nodes)

    return os.path.dirname(node.abspath)


def regex_find_node(regex, nodes):
    for node in nodes:
        if re.match(pattern=regex, string=str(node.abspath)):
            return node

    raise RuntimeError("No file was matched using the specified regex")
