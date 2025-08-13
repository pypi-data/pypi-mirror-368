from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Artifact(BaseModel):
    id: str
    type: str = Field(default="generic")
    name: Optional[str] = None
    uri: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Message(BaseModel):
    id: str | None = None
    role: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    artifact_ids: List[str] = Field(default_factory=list)


class ChatSession(BaseModel):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    artifacts: List[Artifact] = Field(default_factory=list)


# Requests / Responses
class CreateChatResponse(BaseModel):
    session_id: str


class SendMessageRequest(BaseModel):
    user_input: Optional[str] = None
    state: Optional[dict[str, Any]] = None


class NextRequest(BaseModel):
    user_input: Optional[str] = None
    state: Optional[dict[str, Any]] = None


class NextResponse(BaseModel):
    state: dict[str, Any]
    artifacts: List[Artifact]
