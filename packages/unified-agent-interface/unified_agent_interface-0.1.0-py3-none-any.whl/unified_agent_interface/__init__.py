from .app import get_app as get_app  # explicit re-export

__all__ = ["get_app", "cli"]


# Typer CLI entrypoint defined in pyproject as `uai`.
def cli() -> None:  # pragma: no cover
    import json
    import typing as t
    import typer
    import uvicorn

    app = typer.Typer(help="Unified Agent Interface (UAI) CLI")

    def _load_dotenv_if_present() -> None:
        try:
            from dotenv import load_dotenv, find_dotenv  # type: ignore

            env_path = find_dotenv(usecwd=True)
            if env_path:
                load_dotenv(env_path)
        except Exception:
            pass

    @app.command()
    def serve(
        host: str = "0.0.0.0",
        port: int = 8000,
        reload: bool = True,
    ) -> None:
        """Run the UAI FastAPI server."""
        _load_dotenv_if_present()
        uvicorn.run(
            "unified_agent_interface.app:get_app",
            factory=True,
            host=host,
            port=port,
            reload=reload,
        )

    def _http_post(url: str, path: str, json_body: dict) -> dict:
        import httpx  # lazy import

        r = httpx.post(url.rstrip("/") + path, json=json_body, timeout=60)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _http_get(url: str, path: str) -> dict:
        import httpx  # lazy import

        r = httpx.get(url.rstrip("/") + path, timeout=60)
        r.raise_for_status()
        return r.json() if r.text else {}

    def _print(data: t.Any) -> None:
        try:
            typer.echo(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception:
            typer.echo(str(data))

    run_app = typer.Typer(help="Interact with run tasks")
    chat_app = typer.Typer(help="Interact with chat sessions")

    @run_app.command("create")
    def run_create(
        input: str = typer.Option(
            None, "--input", help="Initial run input (string or JSON)"
        ),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
        param: t.List[str] = typer.Option(
            None, "--param", help="Extra param key=value", show_default=False
        ),
    ) -> None:
        params: dict[str, t.Any] = {}
        for p in param or []:
            if "=" in p:
                k, v = p.split("=", 1)
                params[k] = v
        # Try to parse input as JSON if it looks like an object/array
        parsed_input: t.Any = input
        if input and input.strip() and input.strip()[0] in "[{":
            try:
                parsed_input = json.loads(input)
            except Exception:
                parsed_input = input
        payload = {"input": parsed_input, "params": params or None}
        _load_dotenv_if_present()
        data = _http_post(url, "/run/", payload)
        _print(data)

    @run_app.command("status")
    def run_status(
        task_id: str = typer.Argument(..., help="Task ID"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_get(url, f"/run/{task_id}")
        _print(data)

    @run_app.command("input")
    def run_input(
        task_id: str = typer.Argument(..., help="Task ID"),
        text: str = typer.Option(..., "--text", help="Input text"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_post(url, f"/run/{task_id}/input", {"input": text})
        _print(data)

    @run_app.command("logs")
    def run_logs(
        task_id: str = typer.Argument(..., help="Task ID"),
        message: str = typer.Option(..., "--message", help="Log message"),
        level: str = typer.Option("INFO", "--level", help="Log level"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_post(
            url, f"/run/{task_id}/logs", {"level": level, "message": message}
        )
        _print(data)

    @run_app.command("watch")
    def run_watch(
        task_id: str = typer.Argument(..., help="Task ID"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
        interval: float = typer.Option(
            1.0, "--interval", help="Polling interval seconds"
        ),
        verbose: bool = typer.Option(
            True, "--verbose/--quiet", help="Print status changes"
        ),
    ) -> None:
        """Watch a run, prompting for input when required, until completion."""
        import time as _time

        _load_dotenv_if_present()
        prev_status = None
        prev_len = None
        try:
            while True:
                data = _http_get(url, f"/run/{task_id}")
                status = data.get("status")
                ibuf = data.get("input_buffer") or []
                prompt = data.get("input_prompt") or None

                if verbose and (
                    status != prev_status
                    or (
                        isinstance(ibuf, list)
                        and prev_len is not None
                        and len(ibuf) != prev_len
                    )
                ):
                    typer.echo(
                        f"status={status} inputs={len(ibuf) if isinstance(ibuf, list) else 0}"
                    )
                    if prompt and status == "waiting_input":
                        typer.echo(f"input_prompt: {prompt}")
                prev_status = status
                prev_len = len(ibuf) if isinstance(ibuf, list) else prev_len

                if status in ("completed", "failed", "cancelled"):
                    _print(data)
                    break
                if status == "waiting_input":
                    ask = prompt or "Awaiting human input..."
                    text = typer.prompt(ask)
                    if text.strip() == "":
                        typer.echo("Empty input, not sending. Press Ctrl+C to exit.")
                    else:
                        _http_post(url, f"/run/{task_id}/input", {"input": text})
                    # Continue immediately to re-check status
                    continue
                _time.sleep(max(0.1, interval))
        except KeyboardInterrupt:
            typer.echo("Interrupted")

    @chat_app.command("create")
    def chat_create(
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_post(url, "/chat/", {})
        _print(data)

    @chat_app.command("send")
    def chat_send(
        session_id: str = typer.Argument(..., help="Chat session ID"),
        text: str = typer.Option(..., "--text", help="User message"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_post(url, f"/chat/{session_id}", {"user_input": text})
        _print(data)

    @chat_app.command("messages")
    def chat_messages(
        session_id: str = typer.Argument(..., help="Chat session ID"),
        url: str = typer.Option(
            "http://localhost:8000", "--url", help="Base server URL"
        ),
    ) -> None:
        _load_dotenv_if_present()
        data = _http_get(url, f"/chat/{session_id}/messages")
        _print(data)

    app.add_typer(run_app, name="run")
    app.add_typer(chat_app, name="chat")

    # Worker commands
    worker_app = typer.Typer(help="Manage background worker")

    import procrastinate

    def _install_schema_for_app(papp: procrastinate.App) -> None:
        import typer as _typer

        # Try connector.install first
        with papp.open():
            papp.schema_manager.apply_schema()
            _typer.echo("Procrastinate schema installed (schema_manager.apply_schema)")
            return
        _typer.echo(
            "Procrastinate schema installation failed (schema_manager.apply_schema)"
        )

    @worker_app.command("start")
    def worker_start() -> None:
        """Install schema and start Procrastinate worker (requires DATABASE_URL/PROCRASTINATE_DSN)."""
        from .queue import get_procrastinate_app

        _load_dotenv_if_present()
        papp = get_procrastinate_app()

        # Install schema first (idempotent). If it fails, show error but attempt a connectivity check.
        try:
            _install_schema_for_app(papp)
        except Exception as e:
            typer.echo(f"Schema install failed: {e}")

        # Pre-flight connection check if available
        try:
            with papp.open():
                ok = papp.check_connection()  # type: ignore[no-untyped-call]
                if not ok:
                    raise RuntimeError("Cannot connect to database")
        except Exception as e:
            raise RuntimeError(f"DB connection check failed: {e}")

        # Try common worker APIs across versions
        with papp.open():
            papp.run_worker()  # type: ignore[attr-defined]

    @worker_app.command("install")
    def worker_install() -> None:
        """Install Procrastinate schema into the database."""
        from .queue import get_procrastinate_app

        _load_dotenv_if_present()
        papp = get_procrastinate_app()
        _install_schema_for_app(papp)

    @worker_app.command("check")
    def worker_check() -> None:
        """Check DB connectivity for Procrastinate."""
        from .queue import get_procrastinate_app

        _load_dotenv_if_present()
        papp = get_procrastinate_app()

        ok = False
        err = None
        try:
            # App must be open for checks
            with papp.open():
                print(1)
                ok = bool(papp.check_connection())  # type: ignore
                print(papp.check_connection())
        except Exception as e:
            ok = False
            err = e
        if ok:
            typer.echo("Connection OK")
        else:
            typer.echo(f"Connection FAILED: {err}")

    app.add_typer(worker_app, name="worker")

    app()
