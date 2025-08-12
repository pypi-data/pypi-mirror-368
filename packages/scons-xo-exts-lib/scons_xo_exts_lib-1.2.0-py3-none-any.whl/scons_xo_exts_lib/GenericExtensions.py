#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os

from shutil import rmtree

from SCons.Script import Environment


def execute_command(env: Environment, command: str) -> None:
    result = env.Execute(command)

    if result:
        raise RuntimeError(f"Command failed, given: {command}")


def remove(path: str, *args, **kwargs):
    pwd = os.getcwd()

    rmtree(os.path.join(pwd, path), *args, **kwargs)


def find_remove(env: Environment, file_name: str):
    find_exe = env.get("FIND_EXE", "find")

    rm_exe = env.get("RM_EXE", "rm")
    rm_flags = env.get("RM_FLAGS", "-f -r")
    rm_cmd = f"{rm_exe} {rm_flags}"

    execute_command(
        env,
        f"{find_exe} . -name '{file_name}' -exec {rm_cmd} {{}} +",
    )
