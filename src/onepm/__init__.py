from __future__ import annotations

import sys
from typing import Callable, NoReturn

from onepm.core import OneManager


def make_shortcut(method_name: str) -> Callable[[list[str] | None], NoReturn]:
    def main(args: list[str] | None = None) -> NoReturn:  # type: ignore[misc]
        if args is None:
            args = sys.argv[1:]
        package_manager = OneManager().get_package_manager()
        getattr(package_manager, method_name)(*args)

    return main


pi = make_shortcut("install")
pu = make_shortcut("update")
pun = make_shortcut("uninstall")
pr = make_shortcut("run")
pa = make_shortcut("execute")
