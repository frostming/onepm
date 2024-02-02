from __future__ import annotations

import sys
from functools import partial
from typing import NoReturn

from onepm.core import OneManager


def shim(package_manager: str, args: list[str] | None = None) -> NoReturn:
    if args is None:
        args = sys.argv[1:]
    pm = OneManager().get_package_manager(package_manager)
    pm.execute(*args)


pdm = partial(shim, "pdm")
pipenv = partial(shim, "pipenv")
poetry = partial(shim, "poetry")
