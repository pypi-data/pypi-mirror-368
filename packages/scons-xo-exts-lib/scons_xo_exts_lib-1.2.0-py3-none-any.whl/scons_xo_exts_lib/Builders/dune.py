#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Script import Builder
from SCons.Script import Environment

from scons_xo_exts_lib.BuildSupport import NodeMangling


def _get_dune_project(source: list):
    for source_node in source:
        path = source_node.abspath

        if "dune-project" in path:
            return path

    raise RuntimeError("No dune-project in specified sources")


def _dune_command(env: Environment, args_string: str, cwd: str) -> int:
    dune_exe = env.get("DUNE_EXE", "dune")
    dune_flags = env.get("DUNE_FLAGS", "--display=short")

    cmd = f"{dune_exe} {args_string} {dune_flags}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        cwd=cwd,
        shell=True,
    )

    return result.returncode


def _dune_get_install_prefix(target) -> str:
    """
    Guess the install prefix for "dune install --prefix=...".
    """

    separators = ["/bin/", "/lib/"]

    target_node = NodeMangling.get_first_node(target)
    path = str(target_node)

    try:
        for separator in separators:
            if separator in path:
                substrings = path.split(sep=separator, maxsplit=1)
                prefix = substrings[0]

                return os.path.abspath(prefix)

        raise RuntimeError("Separator not found in target")

    except Exception:
        raise RuntimeError(f"Could not guess prefix, given: {path}")


def dune_build_action(target, source, env) -> int:
    dune_project = _get_dune_project(source=source)
    dune_base_dir = os.path.dirname(dune_project)

    result = _dune_command(
        env=env,
        args_string="build @install",
        cwd=dune_base_dir,
    )

    return result


def dune_image_action(target, source, env) -> int:
    dune_project = _get_dune_project(source=source)
    dune_base_dir = os.path.dirname(dune_project)

    install_prefix = _dune_get_install_prefix(target=target)

    result = _dune_command(
        env=env,
        args_string=f"install --prefix={install_prefix}",
        cwd=dune_base_dir,
    )

    return result


def generate(env: Environment) -> None:
    dune_binary_builder = Builder(action=dune_build_action)
    dune_image_builder = Builder(action=dune_image_action)

    env.Append(
        BUILDERS={
            "DuneBinary": dune_binary_builder,
            "DuneImage": dune_image_builder,
        },
    )


def exists(env: Environment):
    return env.Detect("dune")
