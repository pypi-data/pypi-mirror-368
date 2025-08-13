from __future__ import annotations

from typing import Protocol, Any

from ...models.run import RunTask


class RunAgent(Protocol):
    def name(self) -> str: ...

    def on_create(self, task: RunTask, initial_input: Any | None) -> None:
        """Initialize a task when created."""
        ...

    def on_status(self, task: RunTask) -> None:
        """Advance task status if conditions are met (e.g., time elapsed)."""
        ...

    def on_input(self, task: RunTask, text: str) -> None:
        """Handle external input provided to the task."""
        ...
