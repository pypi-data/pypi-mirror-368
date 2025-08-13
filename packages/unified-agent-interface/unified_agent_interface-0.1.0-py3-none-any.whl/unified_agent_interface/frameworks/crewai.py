from __future__ import annotations

import builtins
from typing import Any

from .base import RuntimeAdapter
from .utils import get_status, poll_for_next_input, post_wait


class CrewAIAdapter(RuntimeAdapter):
    def name(self) -> str:
        return "crewai"

    def supports_chat(self) -> bool:
        return False

    def execute(
        self,
        entrypoint_obj: Any,
        *,
        task_id: str,
        initial_payload: Any | None,
        config_dir: str | None = None,
    ) -> str:
        # Prepare kickoff inputs
        if isinstance(initial_payload, dict):
            kickoff_inputs = initial_payload
        elif isinstance(initial_payload, str):
            kickoff_inputs = {"input": initial_payload}
        else:
            kickoff_inputs = {}

        # Establish baseline for input consumption
        baseline_index = 0
        data = get_status(task_id) or {}
        buf0 = data.get("input_buffer") or []
        if isinstance(buf0, list):
            baseline_index = len(buf0)

        real_input = getattr(builtins, "input")

        def _wait_and_get_input(prompt: str = "") -> str:
            nonlocal baseline_index
            prompt = prompt or "Awaiting human input..."
            post_wait(task_id, prompt)
            value, baseline_index = poll_for_next_input(task_id, baseline_index)
            return value

        try:
            builtins.input = _wait_and_get_input  # type: ignore[assignment]
            result = entrypoint_obj.kickoff(inputs=kickoff_inputs)
            return str(result)
        finally:
            builtins.input = real_input  # type: ignore[assignment]

    def chat_respond(
        self,
        entrypoint_obj: Any,
        *,
        session_id: str,
        user_input: str,
        state: dict | None,
        config_dir: str | None = None,
    ) -> str:
        raise NotImplementedError("CrewAI adapter does not support chat mode")
