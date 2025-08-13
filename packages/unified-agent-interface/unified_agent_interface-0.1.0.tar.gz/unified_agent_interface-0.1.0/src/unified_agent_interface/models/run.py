from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class RunArtifact(BaseModel):
    id: str
    type: str = "generic"
    name: Optional[str] = None
    uri: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = "INFO"
    message: str


class RunTask(BaseModel):
    id: str
    status: str = "pending"  # pending|running|completed|failed|cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion_time: Optional[datetime] = None
    result_text: Optional[str] = None
    input_prompt: Optional[str] = None
    artifacts: List[RunArtifact] = Field(default_factory=list)
    logs: List[LogEntry] = Field(default_factory=list)
    input_buffer: List[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class CreateRunRequest(BaseModel):
    input: Optional[Any] = None
    params: Optional[dict[str, Any]] = None


class CreateRunResponse(BaseModel):
    task_id: str
    estimated_completion_time: Optional[datetime] = None


class RunStatusResponse(BaseModel):
    id: str
    status: str
    created_at: datetime
    estimated_completion_time: Optional[datetime] = None
    result_text: Optional[str] = None
    artifacts: List[RunArtifact]
    logs: List[LogEntry]
    input_prompt: Optional[str] = None
    input_buffer: List[str] = Field(default_factory=list)
