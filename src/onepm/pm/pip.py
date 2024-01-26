from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, NoReturn

from packaging.requirements import Requirement

from onepm.pm.base import PackageManager

if TYPE_CHECKING:
    from onepm.core import OneManager


class Pip(PackageManager):
    name = "pip"

    @classmethod
    def matches(cls, pyproject: dict[str, Any]) -> bool:
        """Fallback package manager, always matches."""
        return True

    @classmethod
    def ensure_executable(cls, core: OneManager, requirement: Requirement) -> str:
        from importlib.metadata import Distribution

        venv = cls.make_venv(Path(".venv"))
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        executable = cls.find_executable("python", venv / bin_dir)
        lib_dir = venv / "lib"
        pip_dist = next(lib_dir.glob("**/site-packages/pip-*-dist.info"))
        dist = Distribution.at(pip_dist)
        if dist.version not in requirement:
            subprocess.run(
                [executable, "-m", "pip", "install", "-U", str(requirement)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return executable

    def _find_requirements_txt(self) -> str | None:
        for filename in ["requirements.txt", "requirements.in"]:
            if os.path.exists(filename):
                return filename
        return None

    def _find_setup_py(self) -> str | None:
        for filename in ["setup.py", "pyproject.toml"]:
            if os.path.exists(filename):
                return filename
        return None

    def get_command(self) -> list[str]:
        return [self.executable, "-m", "pip"]

    def install(self, *args: str) -> NoReturn:
        if not args:
            requirements = self._find_requirements_txt()
            setup_py = self._find_setup_py()
            if requirements:
                expanded_args = ["install", "-r", requirements]
            elif setup_py:
                expanded_args = ["install", "."]
            else:
                raise Exception(
                    "No requirements.txt or setup.py/pyproject.toml is found, "
                    "please specify packages to install."
                )
        else:
            expanded_args = ["install", *args]
        self.execute(*expanded_args)

    def update(self, *args: str) -> NoReturn:
        raise NotImplementedError("pip does not support the `pu` shortcut.")

    def uninstall(self, *args: str) -> NoReturn:
        self.execute("uninstall", *args)

    def run(self, *args: str) -> NoReturn:
        if len(args) == 0:
            raise Exception("Please specify a command to run.")
        command, *rest = args
        bin_dir = os.path.dirname(self.executable)
        path = os.getenv("PATH", "")
        command = self.find_executable(command, os.pathsep.join([bin_dir, path]))
        self._execute_command([command, *rest])
