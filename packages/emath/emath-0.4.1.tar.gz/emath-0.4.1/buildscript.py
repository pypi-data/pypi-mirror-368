from __future__ import annotations

__all__ = ()

try:
    from codegen import generate_math_files
except ImportError:
    generate_math_files = None  # type: ignore

import os
import shutil
import sys
from pathlib import Path

from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext

_coverage_compile_args = []
_coverage_links_args = []
if os.environ.get("EMATH_BUILD_WITH_COVERAGE", "0") == "1":
    if os.name == "nt":
        print("Cannot build with coverage on windows.")
        sys.exit(1)
    _coverage_compile_args = ["-fprofile-arcs", "-ftest-coverage", "-O0"]
    _coverage_links_args = ["-fprofile-arcs"]


_emath = Extension(
    "emath._emath",
    libraries=[] if os.name == "nt" else ["stdc++"],
    include_dirs=["vendor/glm", "src/emath", "include"],
    sources=["src/emath/_emath.cpp"],
    language="c++11",
    extra_compile_args=_coverage_compile_args + ([] if os.name == "nt" else ["-std=c++11", "-w"]),
    extra_link_args=_coverage_links_args + ([] if os.name == "nt" else ["-lstdc++"]),
)


_test_api = Extension(
    "emath._test_api",
    include_dirs=["include"],
    sources=["src/emath/_test_api.c"],
    language="c",
    extra_compile_args=_coverage_compile_args,
    extra_link_args=_coverage_links_args,
)


def _build() -> None:
    if os.environ.get("EMATH_GENERATE_MATH_FILES", "0") == "1" and generate_math_files is not None:
        generate_math_files(Path("src/emath"), Path("include"), Path("doc/source"))

    cmd = build_ext(Distribution({"name": "extended", "ext_modules": [_emath, _test_api]}))
    cmd.ensure_finalized()
    cmd.run()
    for output in cmd.get_outputs():
        dest = str(Path("src/emath/") / Path(output).name)
        print(f"copying {output} to {dest}...")
        shutil.copyfile(output, dest)


if __name__ == "__main__":
    _build()
