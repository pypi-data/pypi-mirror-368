# This is a modified version of pre_commit/languages/golang.py
# (https://github.com/pre-commit/pre-commit/blob/main/pre_commit/languages/golang.py)
# from pre-commit (https://github.com/pre-commit/pre-commit). License below:

# Copyright (c) 2014 pre-commit dev team: Anthony Sottile, Ken Struys
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from __future__ import annotations

import functools
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib
import urllib.error
import urllib.request
import zipfile
from contextlib import AbstractContextManager, chdir
from pathlib import Path
from tempfile import TemporaryDirectory, TemporaryFile
from typing import IO, Protocol

from proton_mail_trash.utils import set_env


_ARCH_ALIASES = {
    "x86_64": "amd64",
    "i386": "386",
    "aarch64": "arm64",
    "armv8": "arm64",
    "armv7l": "armv6l",
}
_ARCH = platform.machine().lower()
_ARCH = _ARCH_ALIASES.get(_ARCH, _ARCH)


class ExtractAll(Protocol):
    def extractall(self, path: str) -> None: ...


if sys.platform == "win32":  # pragma: win32 cover
    _EXT = "zip"

    def _open_archive(bio: IO[bytes]) -> AbstractContextManager[ExtractAll]:
        return zipfile.ZipFile(bio)
else:  # pragma: win32 no cover
    _EXT = "tar.gz"

    def _open_archive(bio: IO[bytes]) -> AbstractContextManager[ExtractAll]:
        return tarfile.open(fileobj=bio)


@functools.lru_cache
def _infer_go_version() -> str:
    resp = urllib.request.urlopen("https://go.dev/dl/?mode=json")
    return json.load(resp)[0]["version"].removeprefix("go")  # type: ignore[no-any-return]


def _get_url() -> str:
    os_name = platform.system().lower()
    version = _infer_go_version()
    return f"https://dl.google.com/go/go{version}.{os_name}-{_ARCH}.{_EXT}"


def _install_go(dest: Path) -> None:
    try:
        resp = urllib.request.urlopen(_get_url())  # noqa: S310
    except urllib.error.HTTPError as e:  # pragma: no cover
        if e.code == 404:  # noqa: PLR2004
            msg = (
                f"Could not find a version matching your system requirements "
                f"(os={platform.system().lower()}; arch={_ARCH})"
            )
            raise ValueError(
                msg,
            ) from e
        raise
    else:
        with TemporaryFile() as f:
            shutil.copyfileobj(resp, f)
            f.seek(0)

            with _open_archive(f) as archive:
                archive.extractall(dest)  # type: ignore[arg-type]  # noqa: S202
        shutil.move(dest / "go", dest / ".go")


def build(repo_url: str, build_path: str, bin_name: str, bin_dest: Path) -> None:
    if shutil.which("git") is None:
        print(
            "ERROR: git not found. "
            "Please ensure git is installed and available on your PATH. "
            "You can install it here: https://git-scm.com/downloads"
        )
        sys.exit(1)

    with TemporaryDirectory() as tempdir_s, chdir(tempdir_s):
        tempdir = Path(tempdir_s)
        print("Downloading go...")
        _install_go(tempdir)
        go_root = tempdir / ".go"
        go_bin = go_root / "bin"

        print("Downloading git repo...")
        subprocess.run(["git", "clone", repo_url, "repo"], check=True)  # noqa: S603, S607
        env: dict[str, str] = {
            "GOPATH": str(tempdir),
            "GOTOOLCHAIN": "local",
            "GOROOT": str(go_root),
            "PATH": os.pathsep.join((str(go_bin), os.environ["PATH"])),
        }
        with chdir("repo"), set_env(env):
            print("Building...")
            subprocess.run(["go", "build", build_path], check=True)  # noqa: S603, S607
            shutil.move(bin_name, bin_dest)
