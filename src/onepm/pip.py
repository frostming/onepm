from __future__ import annotations

import os
import sys
from typing import NoReturn

from onepm.base import PackageManager


class Pip(PackageManager):
    name = "pip"

    def _ensure_virtualenv(self) -> str:
        this_venv = os.path.abspath(".venv")
        if os.path.exists(this_venv) and os.path.exists(
            os.path.join(this_venv, "pyvenv.cfg")
        ):
            return this_venv
        if "VIRTUAL_ENV" in os.environ:
            return os.environ["VIRTUAL_ENV"]

        try:
            import venv
        except ImportError:
            raise Exception(
                "To use pip, you must activate a virtualenv or create one at `.venv`."
            ) from None
        venv.create(this_venv, with_pip=True)
        return this_venv

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
        venv = self._ensure_virtualenv()
        if sys.platform == "win32":
            bin_dir = "Scripts"
            exe = ".exe"
        else:
            bin_dir = "bin"
            exe = ""
        return [os.path.join(venv, bin_dir, f"python{exe}"), "-m", "pip"]

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
        self._execute_command(list(args))
