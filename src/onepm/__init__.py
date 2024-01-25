from __future__ import annotations

import sys
from typing import Callable, NoReturn

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from onepm.base import PackageManager
from onepm.pdm import PDM
from onepm.pip import Pip
from onepm.pipenv import Pipenv
from onepm.poetry import Poetry

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


PACKAGE_MANAGERS: dict[str, type[PackageManager]] = {
    p.name: p  # type: ignore[type-abstract]
    for p in [Pipenv, PDM, Poetry, Pip]
}


def determine_package_manager() -> type[PackageManager]:
    try:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
    except FileNotFoundError:
        pyproject = {}
    package_manager: str | None = (
        pyproject.get("tool", {}).get("onepm", {}).get("package-manager")
    )
    if package_manager:
        requirement = Requirement(package_manager)
        if (name := canonicalize_name(requirement.name)) in PACKAGE_MANAGERS:
            return PACKAGE_MANAGERS[name]
    for pm in PACKAGE_MANAGERS.values():
        if pm.matches(pyproject):
            return pm
    return Pip


def make_shortcut(method_name: str) -> Callable[[list[str] | None], NoReturn]:
    def main(args: list[str] | None = None) -> NoReturn:  # type: ignore[misc]
        if args is None:
            args = sys.argv[1:]
        package_manager = determine_package_manager()()
        getattr(package_manager, method_name)(*args)

    return main


pi = make_shortcut("install")
pu = make_shortcut("update")
pun = make_shortcut("uninstall")
pr = make_shortcut("run")
pa = make_shortcut("execute")
