from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    project_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    status: Literal["todo", "in_progress", "done"]
    project_id: int = Field(..., ge=1)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=1000)
    status: Literal["todo", "in_progress", "done"] | None = None
