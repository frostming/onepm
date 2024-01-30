from __future__ import annotations

import os
from typing import Any, NoReturn

from onepm.pm.base import PackageManager


class PDM(PackageManager):
    name = "pdm"

    @classmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        if os.path.exists("pdm.lock"):
            return True
        build_backend = pyproject.get("build-system", {}).get("build-backend", "")
        if "pdm" in build_backend:
            return True
        return "pdm" in pyproject.get("tool", {})

    def install(self, *args: str) -> NoReturn:
        if self.has_unknown_args(args, ["p", "project", "G", "group", "L", "lockfile"]):
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
