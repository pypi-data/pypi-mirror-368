from __future__ import annotations

import os
import time
from typing import Any

import httpx


def server_base_url() -> str:
    return os.getenv("UAI_BASE_URL", "http://localhost:8000").rstrip("/")


def post_wait(task_id: str, prompt: str) -> None:
    try:
        httpx.post(
            f"{server_base_url()}/run/{task_id}/wait",
            json={"prompt": prompt},
            timeout=30,
        )
    except Exception:
        pass


def get_status(task_id: str) -> dict[str, Any] | None:
    try:
        r = httpx.get(f"{server_base_url()}/run/{task_id}", timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def poll_for_next_input(
    task_id: str, baseline_index: int, timeout_seconds: int = 300
) -> tuple[str, int]:
    """Poll the server for a new input. Returns (value, new_index)."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        data = get_status(task_id)
        if data:
            buf = data.get("input_buffer") or []
            if isinstance(buf, list) and len(buf) > baseline_index:
                value = str(buf[baseline_index])
                return value, baseline_index + 1
        time.sleep(0.5)
    return "", baseline_index
