#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder


def bazel_action(target, source, env):
    bazel_pkgs = " ".join(str(s) for s in source)

    bazel_exe = env.get("BAZEL_EXE", "bazelisk")
    bazel_flags = env.get("BAZEL_FLAGS", "")

    cmd = f"{bazel_exe} build {bazel_flags} {bazel_pkgs}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env):
    bazel_binary_builder = Builder(action=bazel_action)

    env.Append(BUILDERS={"BazelBinary": bazel_binary_builder})


def exists(env):
    return env.Detect("bazel")
