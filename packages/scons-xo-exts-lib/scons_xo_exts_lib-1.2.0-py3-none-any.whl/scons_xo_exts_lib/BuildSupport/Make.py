#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from typing import List

from SCons.Script import Environment

from .GenericExtensions import execute_command


def execute_make(env: Environment, args: List[str]) -> None:
    make_cmd = "make" + " ".join(args)

    execute_command(env, make_cmd)
