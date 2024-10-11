from __future__ import annotations

import os
from typing import Any, NoReturn

from onepm.pm.base import PackageManager

UV_INDEX_FLAGS = ["--no-index"]
UV_INSTALLER_FLAGS = ["--reinstall", "--compile-bytecode"]
UV_RESOLVER_FLAGS = ["-U", "--upgrade", "--no-source"]
UV_BUILD_FLAGS = ["--no-build-isolation", "--no-build", "--no-binary"]
UV_CACHE_FLAGS = ["-n", "--no-cache", "--refresh"]
UV_PYTHON_FLAGS = ["--no-python-downloads"]
UV_GLOBAL_FLAGS = [
    "-q",
    "--quiet",
    "-v",
    "--verbose",
    "--native-tls",
    "--offline",
    "--no-progress",
    "--no-config",
    "--help",
    "-V",
    "--version",
]

UV_LOCK_FLAGS = [
    "--locked",
    "--frozen",
    *UV_INDEX_FLAGS,
    *UV_RESOLVER_FLAGS,
    *UV_BUILD_FLAGS,
    *UV_CACHE_FLAGS,
    *UV_PYTHON_FLAGS,
    *UV_GLOBAL_FLAGS,
]
UV_SYNC_FLAGS = [
    "--all-extras",
    "--no-dev",
    "--only-dev",
    "--no-editable",
    "--inexact",
    "--no-install-project",
    "--no-install-workspace",
    *UV_INSTALLER_FLAGS,
    *UV_LOCK_FLAGS,
]


class Uv(PackageManager):
    name = "uv"
    UV_LOCK_FILENAME = "uv.lock"

    @classmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        return os.path.exists(cls.UV_LOCK_FILENAME) or "project" in pyproject

    def install(self, *args: str) -> NoReturn:
        if (
            self.get_unknown_args(args, no_values=UV_SYNC_FLAGS)
            or "-r" in args
            or any(arg.startswith("--requirements") for arg in args)
        ):
            return self.execute("add", *args)
        return self.execute("sync", *args)

    def update(self, *args: str) -> NoReturn:
        if rest_args := self.get_unknown_args(args, no_values=UV_LOCK_FLAGS):
            packages = [name for name in rest_args if not name.startswith("-")]
            args = [arg for arg in args if arg not in packages]
            for package in packages:
                args.extend(["--upgrade-package", package])
            self.execute("lock", *args, exit=False)
        else:
            self.execute("lock", "--upgrade", *args, exit=False)
        self.execute("sync")

    def uninstall(self, *args: str) -> NoReturn:
        return self.execute("remove", *args)

    def run(self, *args: str) -> NoReturn:
        return self.execute("run", *args)
