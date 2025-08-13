from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Tuple


@dataclass
class AgentConfig:
    runtime: str
    entrypoint: str
    adapter: Optional[str]
    raw: dict
    base_dir: str


def _read_toml(path: Path) -> dict:
    try:  # Python >=3.11
        import tomllib  # type: ignore
    except Exception:  # pragma: no cover - fallback if needed
        import tomli as tomllib  # type: ignore
    with path.open("rb") as f:
        return tomllib.load(f)


def load_kosmos_agent_config(path: Optional[str] = None) -> AgentConfig:
    """Load kosmos.toml and return AgentConfig.

    Order of resolution:
    - explicit `path` if provided
    - env var `KOSMOS_TOML`
    - `./kosmos.toml` if exists
    - `./examples/kosmos.toml` if exists
    """
    candidates = []
    if path:
        candidates.append(Path(path))
    env_path = os.getenv("KOSMOS_TOML")
    if env_path:
        candidates.append(Path(env_path))
    candidates.append(Path("kosmos.toml"))
    candidates.append(Path("examples") / "kosmos.toml")

    chosen: Optional[Path] = None
    for p in candidates:
        if p and p.exists():
            chosen = p
            break
    if not chosen:
        raise FileNotFoundError("kosmos.toml not found in expected locations")

    data = _read_toml(chosen)
    agent_section = data.get("agent") or {}
    runtime = agent_section.get("runtime")
    entrypoint = agent_section.get("entrypoint")
    adapter = agent_section.get("adapter") or agent_section.get("adopter")
    if not runtime or not entrypoint:
        raise ValueError(
            "agent.runtime and agent.entrypoint must be set in kosmos.toml"
        )
    return AgentConfig(
        runtime=str(runtime),
        entrypoint=str(entrypoint),
        adapter=str(adapter) if adapter else None,
        raw=agent_section,
        base_dir=str(chosen.parent.resolve()),
    )


def import_entrypoint(
    entrypoint: str, base_dir: Optional[str] = None
) -> Tuple[Any, str, str]:
    """Import `module:attr` and return (obj, module_name, attr_name)."""
    if ":" not in entrypoint:
        raise ValueError("entrypoint must be in 'module:attr' format")
    mod_name, attr_path = entrypoint.split(":", 1)
    mod = None
    # Prefer package import if base_dir is a package
    if base_dir and (Path(base_dir) / "__init__.py").exists() and "." not in mod_name:
        import sys

        package_name = Path(base_dir).name
        sys.path.insert(0, str(Path(base_dir).parent))
        try:
            try:
                mod = importlib.import_module(f"{package_name}.{mod_name}")
            except ModuleNotFoundError:
                mod = None
        finally:
            try:
                sys.path.remove(str(Path(base_dir).parent))
            except ValueError:
                pass

    if mod is None:
        # Try normal import
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            mod = None

    if mod is None:
        # Try file-based import relative to base_dir, then CWD
        from importlib.util import spec_from_file_location, module_from_spec

        paths = []
        if base_dir:
            paths.append(Path(base_dir) / (mod_name.replace(".", os.sep) + ".py"))
        paths.append(Path(mod_name.replace(".", os.sep) + ".py"))
        for candidate in paths:
            if candidate.exists():
                spec = spec_from_file_location(mod_name, candidate)
                if spec and spec.loader:  # type: ignore[truthy-bool]
                    m = module_from_spec(spec)
                    spec.loader.exec_module(m)  # type: ignore[attr-defined]
                    mod = m
                    break
    if mod is None:
        raise ModuleNotFoundError(
            f"Could not import '{mod_name}' from entrypoint '{entrypoint}'"
        )
    obj = mod
    for part in attr_path.split("."):
        obj = getattr(obj, part)
    return obj, mod_name, attr_path
