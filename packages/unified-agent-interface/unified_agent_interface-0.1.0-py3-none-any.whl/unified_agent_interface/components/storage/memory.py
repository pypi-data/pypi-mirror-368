from __future__ import annotations

import uuid
from typing import Dict, List, Optional

from ...models.chat import Artifact, ChatSession, Message
from ...models.run import LogEntry, RunArtifact, RunTask


class InMemoryStorage:
    def __init__(self) -> None:
        self._chats: Dict[str, ChatSession] = {}
        self._runs: Dict[str, RunTask] = {}

    # Chat
    def create_chat(self) -> ChatSession:
        sid = str(uuid.uuid4())
        session = ChatSession(id=sid)
        self._chats[sid] = session
        return session

    def get_chat(self, session_id: str) -> Optional[ChatSession]:
        return self._chats.get(session_id)

    def delete_chat(self, session_id: str) -> bool:
        return self._chats.pop(session_id, None) is not None

    def add_message(self, session_id: str, message: Message) -> None:
        message.id = message.id or str(uuid.uuid4())
        self._chats[session_id].messages.append(message)

    def get_messages(self, session_id: str) -> Optional[List[Message]]:
        session = self._chats.get(session_id)
        return None if session is None else list(session.messages)

    def add_artifact(self, session_id: str, artifact: Artifact) -> None:
        self._chats[session_id].artifacts.append(artifact)

    def get_artifacts(self, session_id: str) -> Optional[List[Artifact]]:
        session = self._chats.get(session_id)
        return None if session is None else list(session.artifacts)

    def get_artifact(self, session_id: str, artifact_id: str) -> Optional[Artifact]:
        session = self._chats.get(session_id)
        if session is None:
            return None
        for art in session.artifacts:
            if art.id == artifact_id:
                return art
        return None

    # Runs
    def create_run(self, initial_input: Optional[object], params: dict) -> RunTask:
        tid = str(uuid.uuid4())
        task = RunTask(
            id=tid,
            status="pending",
            estimated_completion_time=None,
            params=dict(params or {}),
        )
        if isinstance(initial_input, str) and initial_input:
            task.input_buffer.append(initial_input)
        self._runs[tid] = task
        return task

    def get_run(self, task_id: str) -> Optional[RunTask]:
        return self._runs.get(task_id)

    def delete_run(self, task_id: str) -> bool:
        return self._runs.pop(task_id, None) is not None

    def append_run_input(self, task_id: str, text: str) -> None:
        self._runs[task_id].input_buffer.append(text)

    def append_run_log(self, task_id: str, log: LogEntry) -> None:
        self._runs[task_id].logs.append(log)

    def add_run_artifact(self, task_id: str, artifact: RunArtifact) -> None:
        self._runs[task_id].artifacts.append(artifact)

    def get_run_artifacts(self, task_id: str) -> Optional[List[RunArtifact]]:
        task = self._runs.get(task_id)
        return None if task is None else list(task.artifacts)

    def get_single_run_artifact(
        self, task_id: str, artifact_id: str
    ) -> Optional[RunArtifact]:
        task = self._runs.get(task_id)
        if task is None:
            return None
        for art in task.artifacts:
            if art.id == artifact_id:
                return art
        return None
