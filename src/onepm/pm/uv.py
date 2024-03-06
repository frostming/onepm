from __future__ import annotations

import os
from typing import Any, Mapping, NoReturn

from onepm.pm.base import PackageManager


class Uv(PackageManager):
    name = "uv"
    DEFAULT_REQUIREMENT_IN = "pyproject.toml"
    DEFAULT_REQUIREMENT_LOCK = "requirements.lock"

    @classmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        return os.path.exists(cls.DEFAULT_REQUIREMENT_LOCK) or "project" in pyproject

    def _virtualenv_env(self) -> dict[str, str]:
        if "VIRTUAL_ENV" in os.environ or "CONDA_PREFIX" in os.environ:
            return {}
        if not os.path.exists(".venv/pyvenv.cfg"):
            self._execute_command([self.executable, "venv"])
        return {"VIRTUAL_ENV": os.path.join(os.getcwd(), ".venv")}

    def install(self, *args: str) -> NoReturn:
        if self.has_unknown_args(
            args,
            [
                "C",
                "config-setting",
                "only-binary",
                "no-binary",
                "cache-dir",
                "p",
                "python",
                "color",
                "find-links",
                "f",
                "extra-index-url",
                "i",
                "index-url",
            ],
        ):
            return self.execute("pip", "install", *args)
        if os.path.exists(self.DEFAULT_REQUIREMENT_LOCK):
            target = self.DEFAULT_REQUIREMENT_LOCK
        else:
            target = self.DEFAULT_REQUIREMENT_IN
        return self.execute("pip", "sync", *args, target)

    def update(self, *args: str) -> NoReturn:
        self.execute(
            "pip",
            "compile",
            "-o",
            self.DEFAULT_REQUIREMENT_LOCK,
            *args,
            self.DEFAULT_REQUIREMENT_IN,
            exit=False,
        )
        self.execute("pip", "sync", self.DEFAULT_REQUIREMENT_LOCK)

    def uninstall(self, *args: str) -> NoReturn:
        return self.execute("pip", "uninstall", *args)

    def execute(
        self, *args: str, env: Mapping[str, str] | None = None, exit: bool = True
    ) -> Any:
        env = {**self._virtualenv_env(), **(env or {})}
        return super().execute(*args, env=env, exit=exit)

    def run(self, *args: str) -> NoReturn:
        if len(args) == 0:
            raise Exception("Please specify a command to run.")
        command, *rest = args
        env = {**os.environ, **self._virtualenv_env()}

        if "VIRTUAL_ENV" in env:
            bin_dir = os.path.join(
                env["VIRTUAL_ENV"], "Scripts" if os.name == "nt" else "bin"
            )
        elif "CONDA_PREFIX" in env:
            bin_dir = os.path.join(env["CONDA_PREFIX"], "bin")
        else:
            bin_dir = ""
        if bin_dir:
            path = os.pathsep.join([bin_dir, os.getenv("PATH", "")])
        else:
            path = None
        command = self.find_executable(command, path)
        self._execute_command([command, *rest])
