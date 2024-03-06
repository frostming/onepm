from __future__ import annotations

import abc
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Mapping, overload

from packaging.requirements import Requirement

if TYPE_CHECKING:
    from typing import Literal, NoReturn

    from onepm.core import OneManager


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

    @overload
    def execute(
        self,
        *args: str,
        env: Mapping[str, str] | None = ...,
        exit: Literal[False] = ...,
    ) -> None: ...

    @overload
    def execute(
        self, *args: str, env: Mapping[str, str] | None = ..., exit: Literal[True] = ...
    ) -> NoReturn: ...

    def execute(
        self, *args: str, env: Mapping[str, str] | None = None, exit: bool = True
    ) -> Any:
        command_args = self.get_command() + list(args)
        self._execute_command(command_args, env, exit=exit)

    @overload
    @staticmethod
    def _execute_command(
        args: list[str], env: Mapping[str, str] | None = ..., exit: Literal[True] = ...
    ) -> NoReturn: ...

    @overload
    @staticmethod
    def _execute_command(
        args: list[str], env: Mapping[str, str] | None = ..., exit: Literal[False] = ...
    ) -> None: ...

    @staticmethod
    def _execute_command(
        args: list[str], env: Mapping[str, str] | None = None, exit: bool = True
    ) -> Any:
        process_env = {**os.environ, **env} if env else None
        if not exit:
            subprocess.run(args, env=process_env, check=True)
            return
        if sys.platform == "win32":
            sys.exit(subprocess.run(args, env=process_env).returncode)
        else:
            if env:
                os.execvpe(args[0], args, process_env)
            else:
                os.execvp(args[0], args)

    def get_command(self) -> list[str]:
        return [self.executable]

    @abc.abstractmethod
    def install(self, *args: str) -> NoReturn: ...

    @abc.abstractmethod
    def uninstall(self, *args: str) -> NoReturn: ...

    @abc.abstractmethod
    def update(self, *args: str) -> NoReturn: ...

    @abc.abstractmethod
    def run(self, *args: str) -> NoReturn: ...

    @classmethod
    @abc.abstractmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool: ...

    @classmethod
    def get_executable_name(cls) -> str:
        return cls.name

    @classmethod
    def ensure_executable(cls, core: OneManager, requirement: Requirement) -> str:
        name = cls.get_executable_name()
        if not core.shim_enabled():
            return cls.find_executable(name)
        versions = core.get_installations(cls.name)
        best_match = next(
            filter(lambda v: requirement.specifier.contains(v.version), versions), None
        )
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        if best_match is None:
            best_match = core.install_tool(cls.name, requirement)
        return str(best_match.venv / bin_dir / name)

    @staticmethod
    def make_venv(venv_path: Path, with_pip: bool = True) -> Path:
        if venv_path.exists() and venv_path.joinpath("pyvenv.cfg").exists():
            return venv_path

        import venv

        venv.create(venv_path, with_pip=with_pip, symlinks=True)
        return venv_path
