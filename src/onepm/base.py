from __future__ import annotations

import abc
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, NoReturn


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

    def __init__(self) -> None:
        self.command = self.get_command()

    @staticmethod
    def find_executable(name: str, path: str | Path | None = None) -> str:
        # TODO: to keep it simple, only search in PATH(no alias/shell function)
        executable = shutil.which(name, path=path)
        if not executable:
            raise Exception(f"{name} is not found in PATH, did you install it?")
        return executable

    def execute(self, *args: str) -> NoReturn:
        command_args = self.command + list(args)
        self._execute_command(command_args)

    @staticmethod
    def _execute_command(args: list[str]) -> NoReturn:
        if sys.platform == "win32":
            sys.exit(subprocess.run(args).returncode)
        else:
            os.execvp(args[0], args)

    @abc.abstractmethod
    def get_command(self) -> list[str]:
        pass

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
