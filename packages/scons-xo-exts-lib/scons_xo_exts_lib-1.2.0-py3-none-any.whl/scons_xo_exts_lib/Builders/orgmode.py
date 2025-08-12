#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import subprocess

from shutil import move

from SCons.Script import Builder

from scons_xo_exts_lib.BuildSupport import NodeMangling


def _orgmode_extension_to_backend(file_extension: str) -> list[str]:
    match file_extension:
        case "info":
            return "texinfo"
        case "markdown":
            return "md"
        case "pdf":
            return "latex"
        case "texi":
            return "texinfo"
        case _:
            return file_extension


def _orgmode_extension_to_libraries(file_extension: str) -> list[str]:
    elisp_libs = []

    backend = _orgmode_extension_to_backend(file_extension=file_extension)

    if backend != file_extension:
        elisp_libs.append(f"ox-{backend}")

    return elisp_libs


def _orgmode_get_export_flags(target_file: str, source_file: str) -> str:
    file_extension = os.path.splitext(target_file)[1][1:]
    backend = _orgmode_extension_to_backend(file_extension=file_extension)

    if file_extension == "texi":
        fun = "org-texinfo-export-to-texinfo"
    else:
        fun = f"org-{backend}-export-to-{file_extension}"

    load_elisp_libs = [
        "org",
        "ox-latex",
    ]

    extension_libs = _orgmode_extension_to_libraries(file_extension=file_extension)

    load_elisp_libs.extend(extension_libs)

    load_flags = " ".join([f"-l {s}" for s in load_elisp_libs])
    flags = f"{load_flags} {source_file} -f {fun}"

    return flags


def orgmode_action(target, source, env):
    emacs_exe = env.get("EMACS_EXE", "emacs")
    emacs_exec_flags = env.get("EMACS_EXEC_FLAGS", "-batch -q --no-site-file")

    cwd = NodeMangling.get_first_directory(source)

    inp = NodeMangling.get_first_node(source).abspath
    out = NodeMangling.get_first_node(target).abspath

    orgmode_flags = _orgmode_get_export_flags(target_file=out, source_file=inp)
    flags = f"{emacs_exec_flags} {orgmode_flags}"

    cmd = f"{emacs_exe} {flags}"

    print(cmd)

    result = subprocess.run(
        args=cmd,
        capture_output=False,
        check=False,
        shell=True,
        cwd=cwd,
    )

    # When the target basename is different than export basename we have to do
    # a file move.
    if not os.path.exists(out):
        out_extension = os.path.splitext(out)[1]
        inp_basename = os.path.splitext(inp)[0]

        move(f"{inp_basename}{out_extension}", out)

    return result.returncode


def generate(env):
    orgmode_file_builder = Builder(action=orgmode_action)

    env.Append(BUILDERS={"OrgmodeFile": orgmode_file_builder})


def exists(env):
    return env.Detect("orgmode")
