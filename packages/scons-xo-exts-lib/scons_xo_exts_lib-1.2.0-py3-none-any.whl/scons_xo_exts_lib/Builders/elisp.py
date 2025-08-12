#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from SCons.Node import FS

from SCons.Script import Builder
from SCons.Script import Environment

from scons_xo_exts_lib.BuildSupport import NodeMangling


def _elisp_construct_load_path(sources: list) -> str:
    """
    :param sources: list of files to construct a load path from
    :returns: Emacs load path command-line options
    """

    load_path_flags: set[str] = set()

    for source in sources:
        if isinstance(source, FS.File):
            dir_name = source.get_dir().relpath
        else:
            dir_name = os.path.dirname(str(source))

        # Then check if the directory **really** exists.
        if dir_name and os.path.exists(dir_name):
            load_flag = f"-L {dir_name}"

            load_path_flags.add(load_flag)

    return " ".join(load_path_flags)


def _elisp_get_emacs_exe(env: Environment) -> str:
    emacs_exe = env.get("EMACS_EXE")
    emacs_version = env.get("EMACS_VERSION")

    if not emacs_exe:
        if emacs_version:
            return f"emacs-{emacs_version}"

        return "emacs"

    return emacs_exe


def _elisp_get_base_command(env: Environment) -> str:
    exe: str = _elisp_get_emacs_exe(env)

    exec_flags = env.get("EMACS_EXEC_FLAGS", "-batch -q --no-site-file")
    extra_flags = env.get("EMACS_EXTRA_FLAGS", "")

    return f"{exe} {exec_flags} {extra_flags}"


def elisp_autoloads_action(target, source, env) -> int:
    directory = NodeMangling.get_first_directory(source[0])
    out = NodeMangling.get_first_node(target).abspath

    base_args = _elisp_get_base_command(env)

    func = f'loaddefs-generate \\"{directory}\\" \\"{out}\\"'
    flags = f'--eval "({func})"'

    cmd = f"{base_args} {flags}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        cwd=directory,
        shell=True,
    )

    return result.returncode


def elisp_binary_action(target, source, env) -> int:
    srcs: str = " ".join(str(s) for s in source)
    load_path: str = _elisp_construct_load_path(sources=source)

    base_args = _elisp_get_base_command(env)
    comp_flags = env.get("EMACS_COMP_FLAGS", "-L .")

    func = "batch-byte-compile"
    flags = f"{comp_flags} {load_path} -f {func}"

    cmd = f"{base_args} {flags} {srcs}"
    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
    )

    return result.returncode


def generate(env: Environment) -> None:
    autoloads_builder = Builder(action=elisp_autoloads_action)

    binary_builder = Builder(
        action=elisp_binary_action,
        src_suffix=".el",
        suffix=".elc",
    )

    env.Append(
        BUILDERS={
            "ElispAutoloadsFile": autoloads_builder,
            "ElispBinary": binary_builder,
        }
    )


def exists(env: Environment):
    return env.Detect(progs="elisp")
