import os
import sys
from typing import NoReturn, Optional

from onepm.base import PackageManager
from pip import List


class Pip(PackageManager):
    name = "pip"

    def _ensure_virtualenv(self) -> str:
        if "VIRTUAL_ENV" in os.environ:
            return os.environ["VIRTUAL_ENV"]
        this_venv = os.path.abspath(".venv")
        if os.path.exists(this_venv) and os.path.exists(
            os.path.join(this_venv, "pyvenv.cfg")
        ):
            return this_venv
        raise Exception(
            "To use pip, you must activate a virtualenv or create one at `.venv`."
        )

    def _find_requirements_txt(self) -> Optional[str]:
        for filename in ["requirements.txt", "requirements.in"]:
            if os.path.exists(filename):
                return filename
        return None

    def _find_setup_py(self) -> Optional[str]:
        for filename in ["setup.py", "pyproject.toml"]:
            if os.path.exists(filename):
                return filename
        return None

    def get_command(self) -> List[str]:
        venv = self._ensure_virtualenv()
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        return [os.path.join(venv, bin_dir, "python"), "-m", "pip"]

    def install(self, args: List[str]) -> NoReturn:
        if not args:
            requirements = self._find_requirements_txt()
            setup_py = self._find_setup_py()
            if requirements:
                args = ["install", "-r", requirements]
            elif setup_py:
                args = ["install", "."]
            else:
                raise Exception(
                    "No requirements.txt or setup.py/pyproject.toml is found, "
                    "please specify packages to install."
                )
        else:
            args = ["install"] + list(args)
        self.execute_command(args)

    def update(self, args: List[str]) -> NoReturn:
        raise NotImplementedError("pip does not support the `pu` shortcut.")

    def uninstall(self, args: List[str]) -> NoReturn:
        args = ["uninstall"] + list(args)
        self.execute_command(args)

    def run(self, args: List[str]) -> NoReturn:
        self.execute_command(list(args))
