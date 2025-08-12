#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Script import Builder
from SCons.Script import Environment

from scons_xo_exts_lib.BuildSupport import NodeMangling


def _racket_get_plt_user_home(env: Environment) -> str:
    try:
        return env["PLTUSERHOME"]
    except Exception:
        raise RuntimeError("PLTUSERHOME is unset, please set it in SCons")


def _racket_get_raco_exe(env: Environment) -> str:
    racket_exe: str = env.get(key="RACKET_EXE", default="racket")
    raco_exe: str = f"{racket_exe} -l raco --"

    return raco_exe


def _racket_raco(env: Environment, source_node, args: str) -> None:
    plt_user_home: str = _racket_get_plt_user_home(env=env)
    raco: str = _racket_get_raco_exe(env=env)

    extra_variables = {
        "PLTUSERHOME": plt_user_home,
    }

    subprocess_env = env.Clone()["ENV"]
    subprocess_env.update(extra_variables)

    directory: str = NodeMangling.get_first_directory(source_node)
    cmd = f"{raco} {args}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        cwd=directory,
        shell=True,
    )

    if result.returncode == 0:
        return

    raise RuntimeError(f"Raco command failed, ran: {cmd}")


def _racket_install_package(env: Environment, source: list) -> None:
    for source_node in source:
        _racket_raco(
            env=env,
            source_node=source_node,
            args="pkg install --auto --skip-installed --no-docs",
        )


def _racket_setup_package(env: Environment, source: list) -> None:
    for source_node in source:
        _racket_raco(
            env=env,
            source_node=source_node,
            args="setup --tidy --avoid-main --no-docs",
        )


def _racket_create_exe(env: Environment, target, source) -> None:
    for target_node, source_node in zip(target, source):
        out: str = target_node.abspath
        inp: str = source_node.abspath

        _racket_raco(
            env=env,
            source_node=source_node,
            args=f"exe -v --orig-exe -o {out} {inp}",
        )


def racket_library_action(target, source, env) -> int:
    try:
        _racket_install_package(env=env, source=source)
    except RuntimeError:
        return 1

    return 0


def racket_binary_action(target, source, env) -> int:
    try:
        _racket_install_package(env=env, source=source)
        _racket_setup_package(env=env, source=source)
        _racket_create_exe(env=env, target=target, source=source)
    except RuntimeError:
        return 1

    return 0


def generate(env: Environment) -> None:
    racket_binary_builder = Builder(action=racket_binary_action)
    racket_library_builder = Builder(action=racket_library_action)

    env.Append(
        BUILDERS={
            "RacketBinary": racket_binary_builder,
            "RacketLibrary": racket_library_builder,
        }
    )


def exists(env: Environment):
    return env.Detect(progs="racket")
