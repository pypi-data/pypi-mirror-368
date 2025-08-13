from __future__ import annotations

import os
from contextlib import contextmanager

from fastapi.testclient import TestClient


@contextmanager
def _temp_env(**env):
    old = {k: os.getenv(k) for k in env}
    try:
        for k, v in env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_custom_adapter_chat_session():
    from unified_agent_interface.app import get_app

    with _temp_env(
        KOSMOS_TOML=os.path.join("examples", "custom_adapter", "kosmos.toml"),
        UAI_PROCRASTINATE_INLINE="1",
    ):
        client = TestClient(get_app())

        # Create chat session
        r = client.post("/chat/")
        assert r.status_code == 200
        session_id = r.json()["session_id"]

        # First message
        r = client.post(f"/chat/{session_id}", json={"user_input": "hello"})
        assert r.status_code == 200
        body = r.json()
        msgs = body.get("messages") or []
        assert len(msgs) == 2  # user + assistant
        assert any(
            m.get("role") == "assistant" and "echo:" in (m.get("content") or "")
            for m in msgs
        )

        # Second message to verify simple session state increments
        r = client.post(f"/chat/{session_id}", json={"user_input": "again"})
        assert r.status_code == 200
        body = r.json()
        msgs = body.get("messages") or []
        assert len(msgs) == 2
        # Expect n=2 in response content
        assert any(
            m.get("role") == "assistant" and "(n=2)" in (m.get("content") or "")
            for m in msgs
        )
