import os
import sys
from typing import Callable, Dict, NoReturn, Type

from onepm.base import PackageManager
from onepm.pdm import PDM
from onepm.pip import Pip
from onepm.pipenv import Pipenv
from onepm.poetry import Poetry

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


PACKAGE_MANAGERS: Dict[str, Type[PackageManager]] = {
    p.name: p for p in [Pip, Pipenv, Poetry, PDM]
}


def determine_package_manager() -> str:
    pyproject_file = "pyproject.toml"
    if not os.path.exists(pyproject_file):
        return "pip"
    with open(pyproject_file, "rb") as f:
        pyproject_data = tomllib.load(f)
    if os.path.exists("pdm.lock"):
        return "pdm"
    if os.path.exists("poetry.lock"):
        return "poetry"
    if os.path.exists("Pipfile.lock") or os.path.exists("Pipfile"):
        return "pipenv"
    if "pdm" in pyproject_data.get("tool", {}):
        return "pdm"
    if "poetry" in pyproject_data.get("tool", {}):
        return "poetry"
    return "pip"


def make_shortcut(method_name: str) -> Callable[[], NoReturn]:
    def main() -> NoReturn:
        package_manager = PACKAGE_MANAGERS[determine_package_manager()]()
        getattr(package_manager, method_name)(sys.argv[1:])

    return main


pi = make_shortcut("install")
pu = make_shortcut("update")
pun = make_shortcut("uninstall")
pr = make_shortcut("run")
pa = make_shortcut("execute_command")
