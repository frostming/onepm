# Local copy of mina_build.hooks
# https://github.com/GreyElaina/mina/blob/main/src/mina_backend/hooks.py

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Mapping, MutableMapping

from pdm.backend.config import Config
from pdm.backend.hooks import Context

if sys.version_info >= (3, 11):
    import tomllib as tomli
else:
    from pdm.backend._vendor import tomli


def pdm_build_hook_enabled(context: Context) -> bool:
    tool_mina = context.config.data.get("tool", {}).get("mina", {})
    return bool(tool_mina.get("enabled"))


def _get_build_target(context: Context) -> str | None:
    tool_mina = context.config.data.get("tool", {}).get("mina", {})
    return (
        context.config_settings.get("mina-target")
        or os.environ.get("MINA_BUILD_TARGET")
        or tool_mina.get("default-build-target")
    )


def _using_override(config: Config, package_conf: dict[str, Any]) -> bool:
    if "override" in package_conf:
        return package_conf["override"]
    return config.data.get("tool", {}).get("mina", {}).get("override-global", False)


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

    build_config = config.build_config

    # Override build config
    build_config.update(package_conf)

    if using_override:
        config.data["project"] = package_metadata
    else:
        deep_merge(config.metadata, package_metadata)
        # dependencies are already merged, restore them
        config.metadata["dependencies"] = package_metadata.get("dependencies", [])
        config.metadata["optional-dependencies"] = package_metadata.get(
            "optional-dependencies", {}
        )

    config.validate()


def deep_merge(source: MutableMapping, target: Mapping) -> Mapping:
    for key, value in target.items():
        if key in source and isinstance(value, list):
            source[key].extend(value)
        elif key in source and isinstance(value, dict):
            deep_merge(source[key], value)
        else:
            source[key] = value
    return source


def pdm_build_initialize(context: Context) -> None:
    if not pdm_build_hook_enabled(context):
        return

    mina_target = _get_build_target(context)
    if mina_target is None:
        return

    _update_config(context.config, mina_target)
    # Disable mina after update
    context.config.data.setdefault("tool", {}).setdefault("mina", {})["enabled"] = False
