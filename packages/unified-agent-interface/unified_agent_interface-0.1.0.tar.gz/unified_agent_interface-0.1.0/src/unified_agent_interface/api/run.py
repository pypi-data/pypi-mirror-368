from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from ..components.storage.base import Storage
from ..models.run import (
    CreateRunRequest,
    CreateRunResponse,
    LogEntry,
    RunArtifact,
    RunStatusResponse,
)


router = APIRouter()


def get_storage(req: Request) -> Storage:
    return req.app.state.storage


@router.post("/", response_model=CreateRunResponse)
def create_run(
    payload: CreateRunRequest | None = None,
    storage: Storage = Depends(get_storage),
    req: Request = None,
):
    params = (payload.params if payload else None) or {}
    task = storage.create_run(
        initial_input=payload.input if payload else None, params=params
    )
    # Use configured run agent (from kosmos.toml)
    agent = req.app.state.run_agent  # type: ignore[attr-defined]
    agent.on_create(task, payload.input if payload else None)
    return CreateRunResponse(
        task_id=task.id, estimated_completion_time=task.estimated_completion_time
    )


@router.get("/{task_id}", response_model=RunStatusResponse)
def get_run_status(
    task_id: str, storage: Storage = Depends(get_storage), req: Request = None
) -> RunStatusResponse:
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # Advance task by configured agent rules
    agent = req.app.state.run_agent  # type: ignore[attr-defined]
    agent.on_status(task)
    return RunStatusResponse(**task.model_dump())


@router.delete("/{task_id}")
def cancel_run(task_id: str, storage: Storage = Depends(get_storage)):
    ok = storage.delete_run(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}


@router.post("/{task_id}/input")
def provide_input(
    task_id: str,
    payload: CreateRunRequest,
    storage: Storage = Depends(get_storage),
    req: Request = None,
):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.append_run_input(task_id, payload.input or "")
    agent = req.app.state.run_agent  # type: ignore[attr-defined]
    agent.on_input(task, payload.input or "")
    # Resume running
    task.status = "running"
    return {"ok": True}


@router.get("/{task_id}/artifacts", response_model=List[RunArtifact])
def list_run_artifacts(
    task_id: str, storage: Storage = Depends(get_storage)
) -> List[RunArtifact]:
    arts = storage.get_run_artifacts(task_id)
    if arts is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return arts


@router.get("/{task_id}/artifacts/{artifact_id}", response_model=RunArtifact)
def get_run_artifact(
    task_id: str, artifact_id: str, storage: Storage = Depends(get_storage)
) -> RunArtifact:
    art = storage.get_single_run_artifact(task_id, artifact_id)
    if art is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art


@router.post("/{task_id}/logs")
def send_logs(task_id: str, payload: LogEntry, storage: Storage = Depends(get_storage)):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.append_run_log(task_id, payload)
    return {"ok": True}


@router.post("/{task_id}/wait")
def wait_for_input(
    task_id: str, payload: dict, storage: Storage = Depends(get_storage)
):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "waiting_input"
    task.estimated_completion_time = None
    task.input_prompt = str(payload.get("prompt") or "")
    return {"ok": True}


@router.post("/{task_id}/complete")
def complete_run(
    task_id: str,
    payload: dict,  # expects {status: completed|failed, result_text?: str}
    storage: Storage = Depends(get_storage),
):
    task = storage.get_run(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    status = payload.get("status")
    if status not in ("completed", "failed"):
        raise HTTPException(status_code=400, detail="Invalid status")
    task.status = status
    task.result_text = payload.get("result_text")
    task.estimated_completion_time = None
    return {"ok": True}
