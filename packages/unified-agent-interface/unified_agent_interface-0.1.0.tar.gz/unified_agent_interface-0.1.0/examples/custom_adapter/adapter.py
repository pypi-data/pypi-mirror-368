from __future__ import annotations

from typing import Any, Dict, Tuple
from unified_agent_interface.frameworks.base import RuntimeAdapter


class MyCustomAdapter(RuntimeAdapter):
    """A minimal custom adapter demonstrating the RuntimeAdapter protocol.

    - Implements run: echoes inputs without needing the entrypoint.
    - Implements chat: maintains simple per-session state and echoes replies.
    - Does not depend on external frameworks, so it's safe for tests.
    """

    def __init__(self) -> None:
        # (config_dir, session_id) -> message count
        self._sessions: Dict[Tuple[str, str], int] = {}

    # ---- Required RuntimeAdapter methods ----
    def name(self) -> str:
        return "custom.echo"

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        # Ignore entrypoint and just echo the payload
        if isinstance(initial_payload, dict):
            return f"processed-dict:{initial_payload}"
        return f"processed:{initial_payload}"

    def supports_chat(self) -> bool:
        return True

    def chat_respond(
        self,
        entrypoint_obj_or_path: Any,
        *,
        session_id: str,
        user_input: str,
        state: dict | None,
        config_dir: str | None = None,
    ) -> str:
        key = (str(config_dir or ""), session_id)
        n = self._sessions.get(key, 0) + 1
        self._sessions[key] = n
        return f"echo: {user_input} (n={n})"
