from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, JsonValue


class ExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: dict[str, JsonValue] = Field(default_factory=dict)


class ExecuteResult(BaseModel):
    execution_id: int
    status: str
    output: JsonValue = None
    error: str | None = None
    cause: str | None = None
    last_state: str | None = None


class ExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    workflow_id: int
    status: str
    input: JsonValue
    output: JsonValue
    error: str | None
    current_state: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    execution_id: int
    event_order: int
    state_name: str | None
    state_type: str | None
    status: str
    input: JsonValue
    output: JsonValue
    error: str | None
    cause: str | None
    retry_attempt: int
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
