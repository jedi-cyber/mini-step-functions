from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, JsonValue, field_validator
from app.engine.engine import WorkflowEngine


class WorkflowWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    definition: dict[str, JsonValue]
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def valid_name(cls, value):
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return value.strip()



class WorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None
    definition: dict[str, JsonValue]
    is_active: bool
    id: int
    created_at: datetime
    updated_at: datetime
