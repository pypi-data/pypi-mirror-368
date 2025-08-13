from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RuntimeAdapter(Protocol):
    def name(self) -> str: ...

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        """Run the framework using the given entrypoint and return result text.

        Implementations should raise exceptions on failure; callers capture and report.
        """
        ...

    # Optional chat interface; implementations that don't support chat should raise
    # NotImplementedError in chat_respond() and return False in supports_chat().
    def supports_chat(self) -> bool: ...

    def chat_respond(
        self,
        entrypoint_obj: Any,
        *,
        session_id: str,
        user_input: str,
        state: dict | None,
        config_dir: str | None = None,
    ) -> str: ...
