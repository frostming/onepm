from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
from dataclasses import dataclass
from functools import cached_property
from importlib.metadata import Distribution
from pathlib import Path
from typing import TYPE_CHECKING, Any

import tomlkit
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import Version

from onepm.pm.base import PackageManager
from onepm.pm.pdm import PDM
from onepm.pm.pip import Pip
from onepm.pm.pipenv import Pipenv
from onepm.pm.poetry import Poetry
from onepm.pm.uv import Uv

if TYPE_CHECKING:
    from unearth import PackageFinder


PACKAGE_MANAGERS: dict[str, type[PackageManager]] = {
    p.name: p  # type: ignore[type-abstract]
    for p in [Pipenv, PDM, Poetry, Uv, Pip]
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
                self.pyproject = tomlkit.load(f)
        except FileNotFoundError:
            self.pyproject = {}

        self._tool_dir = Path.home() / ".onepm"

    def shim_enabled(self) -> bool:
        try:
            import unearth
        except ModuleNotFoundError:
            return False
        return True

    @cached_property
    def package_finder(self) -> PackageFinder:
        if not self.shim_enabled():
            raise ImportError(
                "Package manager shims are disabled, please re-install onepm with '[shims]' extra."
            )

        import unearth

        index_urls = [self.index_url] if self.index_url else []
        return unearth.PackageFinder(index_urls=index_urls)

    def detect_package_manager(
        self, specified: str | None = None
    ) -> tuple[type[PackageManager], Requirement]:
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
        return package_manager, requirement

    def get_package_manager(self, specified: str | None = None) -> PackageManager:
        package_manager, requirement = self.detect_package_manager(specified)
        executable = str(package_manager.ensure_executable(self, requirement))
        return package_manager(executable)

    def package_dir(self, name: str) -> Path:
        return self._tool_dir / "venvs" / name

    def get_installations(self, name: str) -> list[Installation]:
        venvs = self.package_dir(name)
        if not venvs.exists():
            return []
        versions: list[Installation] = []
        for venv in venvs.iterdir():
            candidate = next(
                venv.glob(f"lib/**/site-packages/{name}-*.dist-info"), None
            )
            if candidate is None:
                continue
            versions.append(Installation(name, Distribution.at(candidate), venv))
        return sorted(versions, key=lambda i: i.version, reverse=True)

    def cleanup(self, name: str | None, version: str | None) -> None:
        if name is None:
            shutil.rmtree(self._tool_dir / "venvs", ignore_errors=True)
            return
        if version is not None:
            matched = next(
                (
                    i
                    for i in self.get_installations(name)
                    if i.version == Version(version)
                ),
                None,
            )
            if matched is None:
                raise ValueError(f"No installation of {name}=={version} is found")
            shutil.rmtree(matched.venv)
            return
        package_dir = self.package_dir(name)
        if package_dir.exists():
            shutil.rmtree(package_dir)

    def install_tool(self, name: str, requirement: Requirement) -> Installation:
        best_match = self.package_finder.find_best_match(requirement).best
        if best_match is None:
            raise Exception(f"Cannot find package matching requirement {requirement}")
        version = Version(best_match.version or "")
        installed_versions = self.get_installations(name)
        if (
            installed := next(
                (i for i in installed_versions if i.version == version), None
            )
        ) is not None:
            return installed

        installed_versions.sort(key=Installation.get_access_time)

        if len(installed_versions) >= MAX_VERSION_NUMBER:
            to_remove = installed_versions[
                : len(installed_versions) - MAX_VERSION_NUMBER + 1
            ]
            for v in to_remove:
                shutil.rmtree(v.venv)
        venv_dir = self.package_dir(name) / str(uuid.uuid4())
        self._run_pip("install", f"{name}=={version}", venv=venv_dir)
        dist = Distribution.at(
            next(venv_dir.glob(f"lib/**/site-packages/{name}-*.dist-info"))
        )
        return Installation(name, dist, venv_dir)

    def _run_pip(self, *args: str, venv: Path) -> None:
        venv = PackageManager.make_venv(venv, with_pip=False)
        bin_dir = "Scripts" if sys.platform == "win32" else "bin"
        pip_command = [
            str(venv / bin_dir / "python"),
            "-I",
            str(self._pip_location),
            *args,
        ]
        subprocess.run(
            pip_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    @cached_property
    def _pip_location(self) -> Path:
        try:
            from pip import __file__ as pip_file
        except ImportError:
            pass
        else:
            # copy to the shared location and use it from that
            shared_pip = self._tool_dir / "shared" / "pip"
            if not shared_pip.exists():
                shutil.copytree(Path(pip_file).parent, shared_pip)
            return shared_pip
        # pip is not installed, download the wheel from PyPI
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

    def update_package_manager(self, name: str | None = None) -> None:
        pm, requirement = self.detect_package_manager(name)
        self.install_tool(pm.name, requirement)

    def use_package_manager(self, spec: str) -> None:
        req = Requirement(spec)
        name = canonicalize_name(req.name)
        self.pyproject.setdefault("tool", {}).setdefault("onepm", {})[
            "package-manager"
        ] = str(req)
        with open(self.path / "pyproject.toml", "w") as f:
            tomlkit.dump(self.pyproject, f)
        for installation in self.get_installations(name):
            if installation.version in req.specifier:
                return
        self.install_tool(canonicalize_name(req.name), req)


@dataclass(frozen=True)
class Installation:
    name: str
    distribution: Distribution
    venv: Path

    @property
    def version(self) -> Version:
        return Version(self.distribution.version)

    def get_access_time(self) -> float:
        return self.venv.stat().st_atime
