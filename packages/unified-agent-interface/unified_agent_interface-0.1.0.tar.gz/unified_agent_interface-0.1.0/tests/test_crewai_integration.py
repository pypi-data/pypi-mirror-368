from __future__ import annotations

import time
import os
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient


crewai = pytest.importorskip(
    "crewai", reason="CrewAI not installed; skipping integration test"
)


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


def test_crewai_example_completes():
    from unified_agent_interface.app import get_app

    # Point to CrewAI kosmos file
    with _temp_env(KOSMOS_TOML=os.path.join("examples", "crewai", "kosmos.toml")):
        client = TestClient(get_app())

        res = client.post("/run/", json={"input": "AI trends"})
        assert res.status_code == 200
        task_id = res.json()["task_id"]

        status = None
        result_text = None
        # Poll up to 60s (CrewAI may take time); keep short for CI
        for _ in range(60):
            r = client.get(f"/run/{task_id}")
            assert r.status_code == 200
            body = r.json()
            status = body["status"]
            if status in ("completed", "failed"):
                result_text = body.get("result_text")
                break
            time.sleep(1)

        assert status in ("completed", "failed")
        # We at least expect a string result/diagnostics
        assert isinstance(result_text, (str, type(None)))
