#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder


def cmake_action(target, source, env):
    cmake_targets = " ".join(str(t) for t in target)

    cmake_exe = env.get("CMAKE_EXE", "cmake")
    cmake_flags = env.get("CMAKE_FLAGS", "")

    cmd = f"{cmake_exe} {cmake_flags} {cmake_targets}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env):
    cmake_binary_builder = Builder(action=cmake_action)

    env.Append(BUILDERS={"CmakeBinary": cmake_binary_builder})


def exists(env):
    return env.Detect("cmake")
