from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from ...config import AgentConfig
from ...queue import enqueue_run_execute
from ...models.run import RunTask
from .run_base import RunAgent


class ConfiguredRunAgent(RunAgent):
    """RunAgent that uses kosmos agent config to dispatch to a specific runtime.

    Supported runtimes:
    - "crewai": entrypoint should be a Crew object exposing `.kickoff(inputs=...)`
    - "callable": entrypoint is a Python callable; called with `(inputs: dict)`
    """

    def __init__(self, cfg: AgentConfig, eta_seconds: int = 5) -> None:
        self.cfg = cfg
        self._eta_seconds = eta_seconds
        self._threads: Dict[str, threading.Thread] = {}

    def name(self) -> str:  # Reflect configured runtime
        return f"configured:{self.cfg.runtime}"

    def _start_thread(self, task: RunTask, target):
        t = threading.Thread(target=target, daemon=True)
        self._threads[task.id] = t
        t.start()

    def on_create(self, task: RunTask, initial_input: Any | None) -> None:
        task.status = "running"
        task.params["agent"] = self.name()
        task.estimated_completion_time = datetime.utcnow() + timedelta(
            seconds=self._eta_seconds
        )

        # Defer execution to Procrastinate worker (or inline in tests)
        try:

            def _inline_complete(status: str, result_text: Optional[str]):
                task.status = status
                task.result_text = result_text
                task.estimated_completion_time = None

            enqueue_run_execute(
                task_id=task.id,
                initial_payload=initial_input,
                inline_complete=_inline_complete,
            )
        except Exception as e:
            task.status = "failed"
            task.result_text = f"Queue error: {e}"
            task.estimated_completion_time = None

    def on_status(self, task: RunTask) -> None:
        t = self._threads.get(task.id)
        if t and not t.is_alive() and task.status == "running":
            task.status = "completed"
            task.estimated_completion_time = None

    def on_input(self, task: RunTask, text: str) -> None:
        # No-op: server already appended input to buffer; worker polls it.
        return
