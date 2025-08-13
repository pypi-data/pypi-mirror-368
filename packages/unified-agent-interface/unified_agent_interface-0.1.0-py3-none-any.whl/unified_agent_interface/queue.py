from __future__ import annotations

import os
from typing import Optional, Callable, Any

from .config import import_entrypoint, load_kosmos_agent_config
from .frameworks import get_adapter

_app = None  # procrastinate.App, initialized lazily


def _load_connector():  # pragma: no cover - exercised via integration usage
    try:
        from procrastinate import PsycopgConnector  # type: ignore
    except Exception as e:  # pragma: no cover - env-specific
        raise RuntimeError(f"psycopg connector not available: {e}")
    return PsycopgConnector(
        kwargs={
            "host": "localhost",
            "user": "postgres",
            "password": "password",
        }
    )


def get_procrastinate_app():  # pragma: no cover - thin wrapper
    global _app
    if _app is not None:
        return _app
    try:
        from procrastinate import App  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"procrastinate not available: {e}")

    connector = _load_connector()
    _app = App(connector=connector)

    @_app.task(name="uai.run.execute")
    def execute(
        task_id: str,
        initial_input: Optional[Any],
        runtime: str,
        entrypoint: str,
        adapter_path: Optional[str] = None,
        config_dir: Optional[str] = None,
        **kwargs,
    ) -> None:
        # Perform the configured run, then call back to server to update status
        status = "completed"
        result_text: Optional[str] = None
        try:
            # Load .env next to kosmos.toml if available
            if config_dir is None:
                config_dir = kwargs.get("config_dir")
            try:
                if config_dir:
                    from dotenv import load_dotenv  # type: ignore
                    from pathlib import Path

                    env_path = Path(config_dir) / ".env"
                    if env_path.exists():
                        load_dotenv(env_path)
            except Exception:
                pass

            obj, _, _ = import_entrypoint(entrypoint, base_dir=config_dir)
            adapter = get_adapter(
                runtime, adapter_path=adapter_path, base_dir=config_dir
            )
            result_text = adapter.execute(
                obj,
                task_id=task_id,
                initial_payload=initial_input,
                config_dir=config_dir,
            )
        except Exception as e:  # pragma: no cover - integration error path
            import traceback as _tb

            status = "failed"
            result_text = f"Error: {e}\n" + _tb.format_exc()

        # Notify server via callback
        base_url = os.getenv("UAI_BASE_URL", "http://localhost:8000").rstrip("/")
        try:
            import httpx

            httpx.post(
                f"{base_url}/run/{task_id}/complete",
                json={"status": status, "result_text": result_text},
                timeout=120,
            ).raise_for_status()
        except Exception:
            # As a last resort, nothing we can do here
            pass

    return _app


def enqueue_run_execute(
    task_id: str,
    initial_payload: Optional[Any],
    inline_complete: Optional[Callable[[str, Optional[str]], Any]] = None,
) -> Optional[str]:
    """Enqueue or directly execute the run task.

    If env var `UAI_PROCRASTINATE_INLINE=1`, executes inline in-process
    (useful for tests or when DB is not accessible). Otherwise, enqueues
    the job to Postgres via Procrastinate and returns the job id.
    """
    cfg = load_kosmos_agent_config()
    runtime = cfg.runtime
    entrypoint = cfg.entrypoint
    config_dir = cfg.base_dir
    adapter_path = (
        getattr(cfg, "adapter", None)
        or cfg.raw.get("adapter")
        or cfg.raw.get("adopter")
    )

    if os.getenv("UAI_PROCRASTINATE_INLINE") == "1":
        # Inline execution in current process: run logic here and call completion callback
        status = "completed"
        result_text: Optional[str] = None
        try:
            obj, _, _ = import_entrypoint(entrypoint, base_dir=config_dir)
            adapter = get_adapter(
                runtime, adapter_path=adapter_path, base_dir=config_dir
            )
            result_text = adapter.execute(
                obj,
                task_id=task_id,
                initial_payload=initial_payload,
                config_dir=config_dir,
            )
        except Exception as e:
            status = "failed"
            result_text = f"Error: {e}"

        if inline_complete:
            inline_complete(status, result_text)
            return None

        # Fallback to HTTP callback if no inline completion available
        base_url = os.getenv("UAI_BASE_URL", "http://localhost:8000").rstrip("/")
        try:
            import httpx

            httpx.post(
                f"{base_url}/run/{task_id}/complete",
                json={"status": status, "result_text": result_text},
                timeout=120,
            ).raise_for_status()
        except Exception:
            pass
        return None

    # Enqueue to worker/DB
    app = get_procrastinate_app()
    with app.open():
        job_id = app.tasks["uai.run.execute"].defer(
            task_id=task_id,
            initial_input=initial_payload,
            runtime=runtime,
            entrypoint=entrypoint,
            adapter_path=adapter_path,
            config_dir=config_dir,
        )
    return str(job_id)
