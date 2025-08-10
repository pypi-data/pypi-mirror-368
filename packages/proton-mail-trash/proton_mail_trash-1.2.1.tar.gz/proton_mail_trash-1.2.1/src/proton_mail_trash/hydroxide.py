from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from time import sleep

from proton_mail_trash import golang
from proton_mail_trash.utils import PopenContext


PATH = Path(__file__).parent / "hydroxide"
if sys.platform == "win32":
    PATH = PATH.with_suffix(".exe")
if sys.platform == "win32":
    CONFIG_PATH = Path(os.getenv("APPDATA"))
else:
    CONFIG_PATH = Path.home() / ".config"
AUTH_PATH = CONFIG_PATH / "hydroxide/auth.json"


def build() -> None:
    if (
        input(
            "I will now bootstrap hydroxide. I only have to do this once. "
            "This is done in an isolated environment.\n"
            "Continue? (y/n) "
        )
        != "y"
    ):
        print("Abort.")
        sys.exit(1)

    bin_name = "hydroxide"
    if sys.platform == "win32":
        bin_name += ".exe"
    golang.build(
        "https://github.com/emersion/hydroxide", "./cmd/hydroxide", bin_name, PATH
    )


def get(user: str) -> Path:
    if not PATH.exists():
        build()
        assert PATH.exists()  # noqa: S101
    if not AUTH_PATH.exists():
        print("Authenticating via Hydroxide, you only have to do this once.")
        subprocess.run([PATH, "auth", user], check=True)  # noqa: S603
        assert AUTH_PATH.exists()  # noqa: S101
        print(
            "Authenticated! Please store the bridge password you got, "
            "you will be prompted for it on each run."
        )
    return PATH


def run_path(hydroxide: Path) -> PopenContext:
    p = PopenContext(
        [hydroxide, "imap"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    sleep(0.25)
    return p


def run(user: str) -> PopenContext:
    return run_path(get(user))
