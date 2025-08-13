from __future__ import annotations

from typing import Protocol, Tuple

from ...models.chat import Artifact, Message


class Agent(Protocol):
    def respond(
        self, session_id: str, user_input: str
    ) -> Tuple[list[Artifact], Message | None]:
        """Session-based chat turn; session holds state internally (framework-managed)."""
        ...

    def next(
        self, state: dict, user_input: str
    ) -> Tuple[dict, list[Artifact], Message | None]:
        """Stateless chat turn; caller provides and receives state updates."""
        ...
