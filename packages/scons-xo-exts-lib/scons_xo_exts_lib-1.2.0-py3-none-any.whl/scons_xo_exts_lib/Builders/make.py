#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder


def make_action(target, source, env):
    make_targets = " ".join(str(t) for t in target)

    make_exe = env.get("MAKE_EXE", "make")
    make_flags = env.get("MAKE_FLAGS", "")

    cmd = f"{make_exe} {make_flags} {make_targets}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env):
    make_binary_builder = Builder(action=make_action)

    env.Append(BUILDERS={"MakeBinary": make_binary_builder})


def exists(env):
    return env.Detect("make")
