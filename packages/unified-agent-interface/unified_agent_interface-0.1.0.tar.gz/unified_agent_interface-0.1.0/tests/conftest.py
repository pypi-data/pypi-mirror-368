from __future__ import annotations

import os
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from unified_agent_interface.app import get_app


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


@pytest.fixture()
def client() -> TestClient:
    # Point the app to a test kosmos.toml that uses a simple callable entrypoint
    with _temp_env(
        KOSMOS_TOML=str(os.path.join("examples", "kosmos_callable.toml")),
        UAI_PROCRASTINATE_INLINE="1",
    ):
        yield TestClient(get_app())
