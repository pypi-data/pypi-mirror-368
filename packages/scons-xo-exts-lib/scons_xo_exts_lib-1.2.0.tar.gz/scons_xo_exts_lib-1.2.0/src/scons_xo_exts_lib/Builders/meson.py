#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Script import Builder

from scons_xo_exts_lib.BuildSupport import NodeMangling


def meson_action(target, source, env):
    source_dir = NodeMangling.get_first_directory(nodes=source)
    builddir = NodeMangling.get_first_directory(nodes=target)

    meson_exe = env.get("MESON_EXE", "meson")
    meson_flags = env.get("MESON_FLAGS", "")

    cmd = f"{meson_exe} setup --reconfigure {meson_flags} {builddir}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        cwd=source_dir,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env):
    meson_builddir_builder = Builder(action=meson_action)

    env.Append(BUILDERS={"MesonBuilddir": meson_builddir_builder})


def exists(env):
    return env.Detect("meson")
