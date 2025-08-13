from __future__ import annotations

from typing import Any, Dict, Tuple
import importlib
import sys

from ..config import import_entrypoint

from .base import RuntimeAdapter


class LangChainAdapter(RuntimeAdapter):
    def name(self) -> str:
        return "langchain"

    def supports_chat(self) -> bool:
        return True

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        # Determine how to send inputs to the chain/runnable
        inputs: Any
        if isinstance(initial_payload, dict):
            inputs = initial_payload
        elif isinstance(initial_payload, str):
            # Common convention: map string input to {"text": "..."}
            inputs = {"text": initial_payload}
        else:
            inputs = {}

        # Prefer LangChain Runnable protocol: .invoke
        if hasattr(entrypoint_obj, "invoke") and callable(
            getattr(entrypoint_obj, "invoke")
        ):
            result = entrypoint_obj.invoke(inputs)
        elif hasattr(entrypoint_obj, "run") and callable(
            getattr(entrypoint_obj, "run")
        ):
            # Legacy LLMChain interface
            try:
                result = entrypoint_obj.run(inputs)
            except TypeError:
                result = entrypoint_obj.run(initial_payload)
        else:
            raise TypeError(
                "Unsupported LangChain entrypoint: expected a Runnable or LLMChain"
            )

        return self._normalize_result(result)

    def chat_respond(
        self,
        entrypoint_obj: Any,
        *,
        session_id: str,
        user_input: str,
        state: dict | None,
        config_dir: str | None = None,
    ) -> str:
        # Map user input to expected fields; include state if provided
        inputs: Any
        base = state.copy() if isinstance(state, dict) else {}
        base.setdefault("text", user_input)
        inputs = base

        inst = self._ensure_session_instance(entrypoint_obj, config_dir, session_id)
        if hasattr(inst, "invoke") and callable(getattr(inst, "invoke")):
            result = inst.invoke(inputs)
        elif hasattr(inst, "run") and callable(getattr(inst, "run")):
            try:
                result = inst.run(inputs)
            except TypeError:
                result = inst.run(user_input)
        else:
            raise TypeError("Unsupported LangChain entrypoint for chat")

        return self._normalize_result(result)

    def _normalize_result(self, result: Any) -> str:
        # Normalize result to string
        try:
            if hasattr(result, "content"):
                return str(getattr(result, "content"))
            if isinstance(result, dict):
                for key in ("text", "output_text", "output", "result"):
                    if key in result:
                        return str(result[key])
            return "" if result is None else str(result)
        except Exception:
            return str(result)

    # Session-scoped instance management
    def __init__(self) -> None:
        self._instances: Dict[Tuple[str, str, str], Any] = {}

    def _ensure_session_instance(
        self, entrypoint_obj: Any, config_dir: str | None, session_id: str
    ) -> Any:
        # When given a string entrypoint, import a fresh instance per (config_dir, entrypoint, session_id)
        if isinstance(entrypoint_obj, str):
            key = (str(config_dir or ""), entrypoint_obj, session_id)
            if key in self._instances:
                return self._instances[key]
            obj, mod_name, attr_path = import_entrypoint(
                entrypoint_obj, base_dir=config_dir
            )
            try:
                if mod_name in sys.modules:
                    m = sys.modules[mod_name]
                    importlib.reload(m)
                    # Re-resolve attribute after reload
                    obj2 = m
                    for part in attr_path.split("."):
                        obj2 = getattr(obj2, part)
                    obj = obj2
            except Exception:
                pass
            self._instances[key] = obj
            return obj

        # If given an object, best-effort reuse (cannot guarantee isolation without factory)
        return entrypoint_obj
