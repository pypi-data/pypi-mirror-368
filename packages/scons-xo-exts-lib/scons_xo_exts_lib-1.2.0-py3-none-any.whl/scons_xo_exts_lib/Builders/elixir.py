#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Script import Builder
from SCons.Script import Environment


def _get_mix_project(source: list):
    for source_node in source:
        path = source_node.abspath

        if "mix.exs" in path:
            return path

    raise RuntimeError("No mix-project in specified sources")


def _mix_command(env: Environment, args_string: str, cwd: str) -> int:
    mix_exe = env.get(key="MIX_EXE", default="mix")
    mix_flags = env.get(key="MIX_FLAGS", default="")

    cmd = f"{mix_exe} {args_string} {mix_flags}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        cwd=cwd,
        shell=True,
    )

    return result.returncode


def elixir_build_action(target, source, env) -> int:
    elixir_project = _get_mix_project(source=source)
    elixir_base_dir = os.path.dirname(elixir_project)

    result = _mix_command(
        env=env,
        args_string="escript.build",
        cwd=elixir_base_dir,
    )

    return result


def generate(env: Environment) -> None:
    elixir_binary_builder = Builder(action=elixir_build_action)

    env.Append(
        BUILDERS={
            "ElixirBinary": elixir_binary_builder,
        },
    )


def exists(env: Environment):
    return env.Detect("elixir")
