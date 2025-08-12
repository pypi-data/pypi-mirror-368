#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import subprocess

from SCons.Script import Builder

from scons_xo_exts_lib.BuildSupport import NodeMangling


def pandoc_action(target, source, env):
    pandoc_exe = env.get("PANDOC_EXE", "pandoc")
    pandoc_flags = env.get("PANDOC_FLAGS", "")

    inp = NodeMangling.get_first_node(source).abspath
    out = NodeMangling.get_first_node(target).abspath

    cmd = f"{pandoc_exe} {pandoc_flags} -o {out} {inp}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env):
    pandoc_file_builder = Builder(action=pandoc_action)

    env.Append(BUILDERS={"PandocFile": pandoc_file_builder})


def exists(env):
    return env.Detect("pandoc")
