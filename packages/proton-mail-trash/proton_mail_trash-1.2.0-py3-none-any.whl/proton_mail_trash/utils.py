from __future__ import annotations

import os
from contextlib import contextmanager
from subprocess import Popen
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Iterator
    from types import TracebackType


class PopenContext(Popen[str]):
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.terminate()
        super().__exit__(exc_type, exc_val, exc_tb)


@contextmanager
def set_env(environ: dict[str, str]) -> Iterator[None]:
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)
