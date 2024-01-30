from __future__ import annotations

import os
from typing import Any, NoReturn

from onepm.pm.base import PackageManager


class Poetry(PackageManager):
    name = "poetry"

    @classmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        if os.path.exists("poetry.lock"):
            return True
        build_backend = pyproject.get("build-system", {}).get("build-backend", "")
        if "poetry" in build_backend:
            return True
        return "poetry" in pyproject.get("tool", {})

    def install(self, *args: str) -> NoReturn:
        if self.has_unknown_args(args, ["E", "extras"]):
            command = "add"
        else:
            command = "install"
        self.execute(command, *args)

    def uninstall(self, *args: str) -> NoReturn:
        self.execute("remove", *args)

    def update(self, *args: str) -> NoReturn:
        self.execute("update", *args)

    def run(self, *args: str) -> NoReturn:
        self.execute("run", *args)
