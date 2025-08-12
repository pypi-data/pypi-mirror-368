#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from SCons.Script import Environment

from ..GenericExtensions import execute_command


def uv_venv_action(target, source, env):
    if os.path.exists(".venv"):
        return
    else:
        env.Execute("${UV_EXE} venv")


def uv_sync_action(target, source, env):
    execute_command(env, "${UV_EXE} sync --all-packages")


def uv_pip(env, cmd):
    execute_command(env, "${UV_EXE} pip " + cmd)


def uv_pip_freeze_action(target, source, env):
    output_file = str(target[0])

    uv_pip(env, f"freeze --exclude-editable > {output_file}")


def uv_build_pkg_action(target, source, env):
    if source:
        flags = " ".join(str(s) for s in source)
    else:
        flags = "--all-packages"

    execute_command(env, "${UV_EXE} build " + flags)


def uv_pytest_action(target, source, env):
    pytest_exec_flags = env.get("PYTEST_FLAGS", "--capture=no")

    execute_command(env, f"${{UV_EXE}} run -- pytest {pytest_exec_flags}")
