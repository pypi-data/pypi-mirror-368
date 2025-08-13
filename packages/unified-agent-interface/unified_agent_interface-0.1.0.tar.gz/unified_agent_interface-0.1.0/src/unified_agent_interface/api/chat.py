from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request

from ..components.agents.base import Agent
from ..components.agents.chat_configured import ConfiguredChatAgent
from ..components.storage.base import Storage
from ..models.chat import (
    Artifact,
    CreateChatResponse,
    Message,
    NextRequest,
    NextResponse,
    SendMessageRequest,
)


router = APIRouter()


def get_storage(req: Request) -> Storage:
    return req.app.state.storage


def get_agent(req: Request) -> Agent:
    # Return app-configured chat agent
    agent = getattr(req.app.state, "chat_agent", None)
    if agent is None:
        raise HTTPException(status_code=501, detail="Chat agent not configured")
    return agent


@router.post("/next", response_model=NextResponse)
def next_step(
    payload: NextRequest, req: Request, agent: Agent = Depends(get_agent)
) -> NextResponse:
    # Stateless chat is not available for LangChain; require a session
    if (
        isinstance(agent, ConfiguredChatAgent)
        and agent.runtime().lower() == "langchain"
    ):
        raise HTTPException(
            status_code=400,
            detail="Stateless chat is not supported for LangChain. Create a session first.",
        )
    state, artifacts, _ = agent.next(payload.state or {}, payload.user_input or "")
    return NextResponse(state=state, artifacts=artifacts)


@router.post("/", response_model=CreateChatResponse)
def create_chat(storage: Storage = Depends(get_storage)) -> CreateChatResponse:
    session = storage.create_chat()
    return CreateChatResponse(session_id=session.id)


@router.post("/{session_id}")
def send_message(
    session_id: str,
    payload: SendMessageRequest,
    storage: Storage = Depends(get_storage),
    agent: Agent = Depends(get_agent),
):
    session = storage.get_chat(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # User message
    user_msg = Message(role="user", content=payload.user_input or "")
    storage.add_message(session_id, user_msg)

    # Agent response (sync; waits and returns reply)
    artifacts, reply = agent.respond(session_id, payload.user_input or "")
    if reply:
        storage.add_message(session_id, reply)

    for art in artifacts:
        storage.add_artifact(session_id, art)

    return {
        "state": {},
        "artifacts": artifacts,
        "messages": [user_msg, reply] if reply else [user_msg],
    }


@router.delete("/{session_id}")
def delete_chat(session_id: str, storage: Storage = Depends(get_storage)):
    ok = storage.delete_chat(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@router.get("/{session_id}/messages", response_model=List[Message])
def get_messages(
    session_id: str, storage: Storage = Depends(get_storage)
) -> List[Message]:
    msgs = storage.get_messages(session_id)
    if msgs is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return msgs


@router.get("/{session_id}/artifacts", response_model=List[Artifact])
def list_artifacts(
    session_id: str, storage: Storage = Depends(get_storage)
) -> List[Artifact]:
    arts = storage.get_artifacts(session_id)
    if arts is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return arts


@router.get("/{session_id}/artifacts/{artifact_id}", response_model=Artifact)
def get_artifact(
    session_id: str, artifact_id: str, storage: Storage = Depends(get_storage)
) -> Artifact:
    art = storage.get_artifact(session_id, artifact_id)
    if art is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return art
