from __future__ import annotations

import subprocess
import sys
from datetime import date, timedelta
from email.parser import HeaderParser
from getpass import getpass
from imaplib import IMAP4
from socket import gethostname

from more_itertools import chunked
from rich.progress import Progress

from proton_mail_trash import hydroxide


PORT = 1143
DELETE_LIMIT = 200


def get_criteria() -> str:
    today = date.today()  # noqa: DTZ011 only using naive datetimes
    interval = timedelta(days=30)

    end = today - interval
    return f"(BEFORE {end.strftime('%d-%b-%Y')})"


def get_to_delete(box: IMAP4) -> list[str]:
    box.select("Trash")
    _typ, data = box.search(None, get_criteria())
    uids = data[0].split()

    mailparser = HeaderParser()
    to_delete = []
    print("### The following messages will be permanently deleted:")
    for uid in uids:
        to_delete.append(uid)
        _resp, data = box.uid("fetch", uid, "(BODY[HEADER])")
        msg = mailparser.parsestr(data[0][1].decode())
        info = f"{msg['From']}, {msg['Date']}, {msg['Subject']}"
        info = info.replace("\n", "").replace("\r", "")
        print(info)

    if (
        input(
            "### The preceding messages will be permanently deleted. Continue? (y/n) "
        )
        != "y"
    ):
        print("Abort.")
        sys.exit(1)

    return to_delete


def delete(box: IMAP4, to_delete: list[str]) -> None:
    with Progress() as progress:
        chunks = list(chunked(to_delete, 200))

        t1 = progress.add_task("Expunging...", total=len(chunks))
        t2 = progress.add_task("Marking...", total=200)

        for chunk in chunks:
            chunk = list(chunk)  # noqa: PLW2901
            progress.update(t2, total=len(chunk))
            for j, uid in enumerate(chunk):
                box.store(uid, "+FLAGS", "\\Deleted")
                progress.update(t2, completed=j + 1)

            box.expunge()
            progress.update(t1, advance=1)


def main() -> None:
    try:
        hostname = gethostname()
        user = (
            subprocess.run(  # noqa: S603
                ["rbw", "get", f"hydroxide {hostname}", "--field", "username"],  # noqa: S607
                check=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )
        password = (
            subprocess.run(  # noqa: S603
                ["rbw", "get", f"hydroxide {hostname}"],  # noqa: S607
                check=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )
    except FileNotFoundError:
        user = None
        password = None

    if not user:
        user = input("E-mail: ")
    with hydroxide.run(user):
        if not password:
            password = getpass("Password: ")

        box = IMAP4("localhost", PORT)
        box.login(user, password)

        to_delete = get_to_delete(box)
        delete(box, to_delete)

        print("Closing...")
        box.close()
        print("Logging out...")
        box.logout()
        print("Stopping Hydroxide...")
