from __future__ import annotations

__all__ = ()

import os
import shutil
import subprocess
import sys
from pathlib import Path
from platform import system

from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext

_coverage_compile_args: list[str] = []
_coverage_links_args: list[str] = []
if os.environ.get("EPLATFORM_BUILD_WITH_COVERAGE", "0") == "1":
    if system() == "Windows":
        print("Cannot build with coverage on windows.")
        sys.exit(1)
    _coverage_compile_args = ["-fprofile-arcs", "-ftest-coverage", "-O0"]
    _coverage_links_args = ["-fprofile-arcs"]

_eplatform = Extension(
    "eplatform._eplatform",
    library_dirs=["vendor/SDL"],
    libraries=["SDL3"],
    include_dirs=["src/eplatform", "vendor/SDL/include", "vendor/emath/include"],
    sources=["src/eplatform/_eplatform.c"],
    extra_compile_args=_coverage_compile_args,
    extra_link_args=_coverage_links_args,
)


def _build_sdl() -> None:
    subprocess.run(
        [
            "cmake",
            ".",
            "-GNinja",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DSDL_TESTS=0",
            "-DSDL_TEST_LIBRARY=0",
        ],
        cwd="vendor/SDL",
        check=True,
    )
    subprocess.run(["cmake", "--build", ".", "--config", "Release"], cwd="vendor/SDL", check=True)


def _build() -> None:
    _build_sdl()
    cmd = build_ext(Distribution({"name": "extended", "ext_modules": [_eplatform]}))
    cmd.ensure_finalized()
    cmd.run()
    for output in cmd.get_outputs():
        dest = str(Path("src/eplatform/") / Path(output).name)
        print(f"copying {output} to {dest}...")
        shutil.copyfile(output, dest)


if __name__ == "__main__":
    if os.environ.get("EPLATFORM_BUILD_EXTENSION", "1") == "1":
        _build()
