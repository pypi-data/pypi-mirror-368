from __future__ import annotations

from typing import Dict, Tuple, Any, Optional

from .base import RuntimeAdapter
from .crewai import CrewAIAdapter
from .callable import CallableAdapter
from .langchain import LangChainAdapter
from ..config import import_entrypoint


_adapters: Dict[str, RuntimeAdapter] = {
    "crewai": CrewAIAdapter(),
    "callable": CallableAdapter(),
    "langchain": LangChainAdapter(),
}

_dynamic_cache: Dict[Tuple[str, str], RuntimeAdapter] = {}


def get_adapter(
    runtime: str, adapter_path: Optional[str] = None, base_dir: Optional[str] = None
) -> RuntimeAdapter:
    rt = (runtime or "").lower()
    # If a custom adapter is specified, prefer it
    if adapter_path:
        key = (adapter_path, str(base_dir or ""))
        if key in _dynamic_cache:
            return _dynamic_cache[key]
        obj, _, _ = import_entrypoint(adapter_path, base_dir=base_dir)
        # If obj is a class, require it to explicitly inherit RuntimeAdapter and instantiate; otherwise assume it's an instance
        inst: Any
        try:
            if isinstance(obj, type):
                # Enforce explicit inheritance from RuntimeAdapter
                if RuntimeAdapter not in obj.__mro__:
                    raise TypeError("Custom adapter class must inherit RuntimeAdapter")
                inst = obj()
            else:
                inst = obj
        except Exception as e:  # pragma: no cover - defensive
            raise TypeError(
                f"Failed to instantiate custom adapter '{adapter_path}': {e}"
            )
        # Validate protocol at runtime as well
        if not isinstance(inst, RuntimeAdapter):
            raise TypeError("Custom adapter must inherit and implement RuntimeAdapter")
        _dynamic_cache[key] = inst  # type: ignore[assignment]
        return inst  # type: ignore[return-value]

    # Built-in adapters
    if rt in _adapters:
        return _adapters[rt]
    raise ValueError(
        f"Unsupported runtime: {runtime}. Provide 'adapter = \"module:attr\"' in kosmos.toml to use a custom adapter."
    )
