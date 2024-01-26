from __future__ import annotations

import abc
import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, NoReturn

from packaging.requirements import Requirement
from packaging.version import Version

if TYPE_CHECKING:
    from onepm.core import OneManager


@lru_cache(maxsize=1)
def wrapper_enabled() -> bool:
    try:
        import unearth  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True


class PackageManager(metaclass=abc.ABCMeta):
    name: str

    @staticmethod
    def has_unknown_args(args: Iterable[str], expecting_values: list[str]) -> bool:
        args_iter = iter(args)

        for arg in args_iter:
            if arg[:2] == "--":
                arg_name = arg[2:]
                if arg_name in expecting_values:
                    next(args_iter, None)
            elif arg[0] == "-":
                arg_name = arg[1:]
                if arg_name in expecting_values:
                    next(args_iter, None)
            else:
                return True
        return False

    def __init__(self, executable: str) -> None:
        self.executable = executable

    @staticmethod
    def find_executable(name: str, path: str | Path | None = None) -> str:
        # TODO: to keep it simple, only search in PATH(no alias/shell function)
        executable = shutil.which(name, path=path)
        if not executable:
            raise Exception(f"{name} is not found in PATH, did you install it?")
        return executable

    def execute(self, *args: str) -> NoReturn:
        command_args = self.get_command() + list(args)
        self._execute_command(command_args)

    @staticmethod
    def _execute_command(args: list[str]) -> NoReturn:
        if sys.platform == "win32":
            sys.exit(subprocess.run(args).returncode)
        else:
            os.execvp(args[0], args)

    def get_command(self) -> list[str]:
        return [self.executable]

    @abc.abstractmethod
    def install(self, *args: str) -> NoReturn:
        pass

    @abc.abstractmethod
    def uninstall(self, *args: str) -> NoReturn:
        pass

    @abc.abstractmethod
    def update(self, *args: str) -> NoReturn:
        pass

    @abc.abstractmethod
    def run(self, *args: str) -> NoReturn:
        pass

    @classmethod
    @abc.abstractmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        pass

    @classmethod
    def get_executable_name(cls) -> str:
        return cls.name

    @classmethod
    def ensure_executable(cls, core: OneManager, requirement: Requirement) -> str:
        name = cls.get_executable_name()
        if not wrapper_enabled():
            # Find in PATH
            return cls.find_executable(name)

        versions = core.get_versions(cls.name)
        best_match = max(
            filter(requirement.specifier.contains, versions), default=None, key=Version
        )
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        if best_match is not None:
            return str(core.package_dir(cls.name) / best_match / bin_dir / name)
        return str(core.install_tool(cls.name, requirement) / bin_dir / name)

    @staticmethod
    def make_venv(venv_path: Path, with_pip: bool = True) -> Path:
        if venv_path.exists() and venv_path.joinpath("pyvenv.cfg").exists():
            return venv_path

        import venv

        venv.create(venv_path, with_pip=with_pip)
        return venv_path