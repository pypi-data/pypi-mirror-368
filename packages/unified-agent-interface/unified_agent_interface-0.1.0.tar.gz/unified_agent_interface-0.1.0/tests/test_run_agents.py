from __future__ import annotations

import time

from fastapi.testclient import TestClient


def test_configured_callable_run_completes(client: TestClient):
    # Create run; agent is selected via kosmos.toml (callable runtime)
    res = client.post("/run/", json={"input": "process this"})
    assert res.status_code == 200
    task_id = res.json()["task_id"]

    # Poll until completed (bounded wait)
    status = None
    result_text = None
    for _ in range(10):
        r = client.get(f"/run/{task_id}")
        assert r.status_code == 200
        body = r.json()
        status = body["status"]
        if status == "completed":
            result_text = body.get("result_text")
            break
        time.sleep(0.2)
    assert status == "completed"
    assert isinstance(result_text, str) and result_text.startswith("processed:")


def test_run_logs_append(client: TestClient):
    # Create run, then append a log entry
    res = client.post("/run/", json={})
    assert res.status_code == 200
    task_id = res.json()["task_id"]

    # Append log
    r = client.post(
        f"/run/{task_id}/logs", json={"level": "INFO", "message": "starting"}
    )
    assert r.status_code == 200

    # Verify status includes logs
    r = client.get(f"/run/{task_id}")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("logs"), list)
    assert any(log.get("message") == "starting" for log in data["logs"])
