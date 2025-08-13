Unified Agent Interface (UAI)
=============================

UAI is a FastAPI service and CLI that exposes a simple, unified API to run different agent frameworks behind a consistent interface. It loads your agent from a `kosmos.toml` file and executes it either inline (for dev/tests) or via a Procrastinate worker.

Quickstart
----------
- Install: `pip install -e .`
- Run API: `uai serve --host 0.0.0.0 --port 8000`
- Open docs: visit `http://localhost:8000/docs`

CLI Overview
------------
- `uai serve`: starts the FastAPI server.
- `uai run create --input '<json or string>'`: creates a run for the configured agent.
- `uai run status <task_id>`: fetches current run status.
- `uai run input <task_id> --text '<reply>'`: provides human input to a waiting run.
- `uai run logs <task_id> --message '<msg>' [--level INFO]`: appends a log entry.
- `uai worker install|check|start`: installs schema, checks DB, and starts the worker.
 - `uai run watch <task_id>`: watches status; when `waiting_input`, prompts for input and resumes automatically.

Project Structure
-----------------
- `src/unified_agent_interface/app.py`: FastAPI app factory.
- `src/unified_agent_interface/api/`: Routers for `/run` and `/chat`.
- `src/unified_agent_interface/models/`: Pydantic models and schemas.
- `src/unified_agent_interface/components/`: In-memory storage and run agent shim.
- `src/unified_agent_interface/frameworks/`: Runtime adapters (`crewai`, `langchain`, `callable`).
- `src/unified_agent_interface/queue.py`: Procrastinate integration and job dispatch.
- `examples/`: Callable sample and CrewAI examples (with and without human input).

Agent Configuration
-------------------
- Location search order: `KOSMOS_TOML` env var, `./kosmos.toml`, `./examples/kosmos.toml`.
- Example config:

  ```toml
  [agent]
  runtime = "callable"  # or "crewai", "langchain", or "custom"
  entrypoint = "examples.simple_entrypoint:run"
  # Optional: for custom adapters
  # adapter = "path.to.module:AdapterClassOrInstance"
  ```

- Entrypoint format: `module:attr` (e.g., `examples.crewai_user_input.main:crew`). UAI resolves imports relative to the `kosmos.toml` directory and also supports package-style modules.
- Custom adapters: set `agent.adapter` to a `module:attr` that resolves to either an instance or a zero-arg class. The adapter must explicitly inherit `unified_agent_interface.frameworks.base.RuntimeAdapter`. If `runtime` is unknown or set to `custom`, UAI will load this adapter. If both a known runtime and an adapter are specified, the adapter takes precedence.

Runtimes (Adapters)
-------------------
- `crewai`: Imports a `Crew` and calls `crew.kickoff(inputs=...)`.
  - Inputs: pass JSON via `--input '{"topic":"..."}'`. Dicts are used as-is; string inputs map to `{ "input": "..." }`.
  - Human input: When the Crew calls `input()`, UAI sets status to `waiting_input` and populates `input_prompt`. Provide input with `uai run input` and the run resumes.
- `langchain`: Imports a LangChain `Runnable`/`LLMChain` and calls `invoke(inputs)` (or `run(...)` fallback).
  - Inputs: dicts are passed as-is. String inputs map to `{ "text": "..." }`.
  - Output: tries `message.content`, then common dict keys (`text`, `output_text`, `output`, `result`), else `str(result)`.
- `callable`: Imports a Python callable.
  - If `--input` is a JSON object, UAI tries `fn(**obj)`, falling back to `fn(obj)`; otherwise it calls `fn({"input": "...", "params": {}})`.
 - `custom`: Provide `adapter = "module:attr"` in `kosmos.toml`; UAI imports and uses it for both run and chat if implemented.

Examples
--------
- Callable: `examples/simple_entrypoint.py` with `examples/kosmos_callable.toml`.
- CrewAI (basic): `examples/crewai/main.py` with `examples/crewai/kosmos.toml`.
- CrewAI (human input): `examples/crewai_user_input/main.py` with `examples/crewai_user_input/kosmos.toml`.
- LangChain (LLMChain): `examples/langchain/app.py` with `examples/langchain/kosmos.toml`.

Run API
-------
- `POST /run/` (body: `{ "input": <any>, "params": <object?> }`): creates a run. `input` may be a string or JSON object/array.
- `GET /run/{id}`: returns status with fields: `status`, `result_text`, `logs`, `artifacts`, `input_prompt`, `input_buffer`.
- `POST /run/{id}/input` (body: `{ "input": "..." }`): appends to `input_buffer` and resumes a waiting run.
- `POST /run/{id}/logs` (body: `{ level, message }`): appends a log.
- `POST /run/{id}/complete` (internal): worker callback to finalize a run.

Chat API
--------
- `POST /chat/`: creates a chat session and returns `{ session_id }`.
- `POST /chat/{session_id}`: sends a user message; responds after generating the assistant reply with `{ state, artifacts, messages }`.
- `GET /chat/{session_id}/messages`: lists messages in the session.
- `DELETE /chat/{session_id}`: deletes the session.

Background Jobs (Procrastinate)
-------------------------------
- Default local DB: If no `PROCRASTINATE_DSN`/`DATABASE_URL` is set, UAI connects to `localhost:5432` with `user=postgres`, `password=password`, `dbname=postgres`.
- Start a local Postgres (optional): `docker run --name pg-procrastinate --detach --rm -p 5432:5432 -e POSTGRES_PASSWORD=password postgres`
- Worker commands:
  - `uai worker install`: installs Procrastinate schema (idempotent).
  - `uai worker check`: verifies DB connectivity.
  - `uai worker start`: auto-installs schema, checks DB, then starts the worker.
- Inline mode (no DB): `UAI_PROCRASTINATE_INLINE=1` executes runs in-process (used in tests).

Environment Variables
---------------------
- `KOSMOS_TOML`: Path to `kosmos.toml` to load agent config.
- `UAI_BASE_URL`: Base URL for server (used by worker callbacks). Defaults to `http://localhost:8000`.
- `UAI_PROCRASTINATE_INLINE`: Set to `1` to run jobs inline without Postgres.
- `PROCRASTINATE_DSN`/`DATABASE_URL`: Postgres connection for the worker. If unset, UAI uses local defaults.
- `PROCRASTINATE_HOST/PORT/USER/PASSWORD/DB`: Overrides for local default connection.

Troubleshooting
---------------
- Import errors: Ensure `KOSMOS_TOML` points to the right example and that the entrypoint’s dependencies (e.g., `crewai`, `langchain_community`) are installed in both server and worker environments.
- PoolTimeout on worker start: Check Docker Postgres is running and accessible; use `uai worker check`. Add required SSL options to your DSN if using a cloud provider (e.g., `?sslmode=require`).
- Human input not progressing: Confirm status shows `waiting_input` with a non-empty `input_prompt`, then send `uai run input <task_id> --text '...'`.

Notes
-----
- Storage is in-memory for now; swap with a persistent backend (Postgres/Redis) for multi-process reliability. The worker currently finalizes runs via a callback to `POST /run/{id}/complete`.
- LangChain chat requires sessions: stateless `POST /chat/next` is not supported and returns 400. UAI maintains a separate chain instance per session to isolate memory.
