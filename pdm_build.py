"""Custom PDM backend build hook for monorepo support.

This is derived from the [Mina](https://github.com/GreyElaina/Mina) project
and should be replaced by the official Mina backend once it is available.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, cast

from pdm.backend._vendor.packaging.requirements import Requirement
from pdm.backend._vendor.packaging.utils import canonicalize_name
from pdm.backend.config import Config
from pdm.backend.hooks import Context

if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    from pdm.backend._vendor import tomli


def _get_build_target(context: Context) -> str | None:
    tool_mina = context.config.data.get("tool", {}).get("mina", {})
    return (
        context.config_settings.get("mina-target")
        or os.environ.get("MINA_BUILD_TARGET")
        or tool_mina.get("default-target")
    )


def _using_override(config: Config, package_conf: dict[str, Any]) -> bool:
    if "override" in package_conf:
        return package_conf["override"]
    return config.data.get("tool", {}).get("mina", {}).get("override-global", False)


def _patch_dep(
    config: Config, pkg_project: dict[str, Any], using_override: bool = False
) -> None:
    if "dependencies" in pkg_project:
        deps = cast(list[str], pkg_project["dependencies"])
        deps_map = {canonicalize_name(Requirement(i).name): i for i in deps}
        workspace_deps = config.metadata.get("dependencies", [])
        if not using_override:
            for dep in workspace_deps:
                req = Requirement(dep)
                if canonicalize_name(req.name) not in deps_map:
                    deps.append(dep)

    if "optional-dependencies" in pkg_project:
        optional_dep_groups: dict[str, list[str]] = pkg_project["optional-dependencies"]

        for group, optional_deps in optional_dep_groups.items():
            workspace_group_deps: list[str] = config.metadata.get(
                "optional-dependencies", {}
            ).get(group, [])
            deps_map = {
                canonicalize_name(Requirement(i).name): i for i in optional_deps
            }
            if not using_override:
                for dep in workspace_group_deps:
                    req = Requirement(dep)
                    if canonicalize_name(req.name) not in deps_map:
                        optional_deps.append(dep)


def _get_standalone_config(root: Path, pkg: str):
    config_file = root / ".mina" / f"{pkg}.toml"
    if not config_file.exists():
        return

    return tomli.loads(config_file.read_text())


def _update_config(config: Config, package: str) -> None:
    package_conf = _get_standalone_config(config.root, package)
    if package_conf is not None:
        package_conf.setdefault("includes", []).append(f".mina/{package}.toml")
    else:
        package_conf = (
            config.data.get("tool", {})
            .get("mina", {})
            .get("packages", {})
            .get(package, None)
        )
        if package_conf is None:
            raise ValueError(f"No package named '{package}'")

    package_metadata = package_conf.pop("project", {})
    using_override = _using_override(config, package_conf)
    _patch_dep(config, package_metadata, using_override)

    build_config = config.build_config

    # Override build config
    build_config.update(package_conf)

    if using_override:
        config.data["project"] = package_metadata
    else:
        deep_merge(config.metadata, package_metadata)

    config.validate(config.data, config.root)


def deep_merge(source: dict, target: dict) -> dict:
    for key, value in target.items():
        if key in source and isinstance(value, list):
            source[key].extend(value)
        elif key in source and isinstance(value, dict):
            deep_merge(source[key], value)
        else:
            source[key] = value
    return source


def pdm_build_initialize(context: Context) -> None:
    mina_target = _get_build_target(context)
    if mina_target is None:
        return
    _update_config(context.config, mina_target)
