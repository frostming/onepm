from __future__ import annotations

import os
import shutil
import subprocess
import sys
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

from onepm.pm.base import PackageManager
from onepm.pm.pdm import PDM
from onepm.pm.pip import Pip
from onepm.pm.pipenv import Pipenv
from onepm.pm.poetry import Poetry

if TYPE_CHECKING:
    from unearth import PackageFinder

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

PACKAGE_MANAGERS: dict[str, type[PackageManager]] = {
    p.name: p  # type: ignore[type-abstract]
    for p in [Pipenv, PDM, Poetry, Pip]
}

MAX_VERSION_NUMBER = 5  # keep 5 versions of each package at most


class OneManager:
    pyproject: dict[str, Any]

    def __init__(
        self, path: Path | None = None, *, index_url: str | None = None
    ) -> None:
        self.path = path or Path.cwd()
        self.index_url = index_url
        try:
            with open(self.path / "pyproject.toml", "rb") as f:
                self.pyproject = tomllib.load(f)
        except FileNotFoundError:
            self.pyproject = {}

        self._tool_dir = Path.home() / ".onepm"

    @cached_property
    def package_finder(self) -> PackageFinder:
        import unearth

        index_urls = [self.index_url] if self.index_url else []
        return unearth.PackageFinder(index_urls=index_urls)

    def get_package_manager(self, specified: str | None = None) -> PackageManager:
        requested: str | None = (
            self.pyproject.get("tool", {}).get("onepm", {}).get("package-manager")
        )
        package_manager: type[PackageManager] | None = None
        requirement: Requirement | None = None
        if requested:
            requirement = Requirement(requested)
            name = canonicalize_name(requirement.name)
            if specified and specified != name:
                name = specified
                requirement = Requirement(specified)
            if name in PACKAGE_MANAGERS:
                package_manager = PACKAGE_MANAGERS[name]
            else:
                raise ValueError(f"Not supported package-manager: {requested}")
        elif specified:
            package_manager = PACKAGE_MANAGERS[specified]
        else:
            for pm in PACKAGE_MANAGERS.values():
                if pm.matches(self.pyproject):
                    package_manager = pm
                    break
        assert package_manager is not None
        if requirement is None:
            requirement = Requirement(package_manager.name)
        executable = str(package_manager.ensure_executable(self, requirement))
        return package_manager(executable)

    def package_dir(self, package: str) -> Path:
        return self._tool_dir / "venvs" / package

    def get_versions(self, name: str) -> list[str]:
        package_manager_dir = self.package_dir(name)
        if not package_manager_dir.exists():
            return []
        return [d.name for d in package_manager_dir.iterdir() if d.is_dir()]

    def cleanup(self, package: str) -> None:
        package_dir = self.package_dir(package)
        if package_dir.exists():
            shutil.rmtree(package_dir)

    def install_tool(self, package: str, requirement: Requirement) -> Path:
        best_match = self.package_finder.find_best_match(requirement).best
        if best_match is None:
            raise Exception(f"Cannot find package matching requirement {requirement}")
        version = best_match.version
        assert version is not None
        version = str(Version(version))  # normalize
        package_venvs_dir = self.package_dir(package) / version
        if not package_venvs_dir.exists():

            def get_access_time(version: str) -> float:
                return package_venvs_dir.with_name(version).stat().st_atime

            versions = sorted(self.get_versions(package), key=get_access_time)
            if len(versions) >= MAX_VERSION_NUMBER:
                to_remove = versions[: len(versions) - MAX_VERSION_NUMBER + 1]
                for v in to_remove:
                    shutil.rmtree(self.package_dir(package) / v)
            self._run_pip("install", f"{package}=={version}", venv=package_venvs_dir)
        return package_venvs_dir

    def _run_pip(self, *args: str, venv: Path) -> None:
        venv = PackageManager.make_venv(venv, with_pip=False)
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        pip_command = [
            str(venv / bin_dir / "python"),
            "-I",
            str(self._get_shared_pip()),
            *args,
        ]
        subprocess.run(
            pip_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _get_shared_pip(self) -> Path:
        shared_pip = self._tool_dir / "shared" / "pip.whl"
        if not shared_pip.exists():
            best_pip = self.package_finder.find_best_match("pip").best
            assert best_pip is not None and best_pip.link.is_wheel
            shared_pip.parent.mkdir(parents=True, exist_ok=True)
            wheel = self.package_finder.download_and_unpack(
                best_pip.link, shared_pip.parent
            )
            os.replace(wheel, shared_pip)
        return shared_pip / "pip"
