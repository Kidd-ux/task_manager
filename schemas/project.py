from pydantic import BaseModel, ConfigDict
from schemas.task import TaskResponse


class ProjectResponse(BaseModel):
    id: int
    name: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str | None = None


class ProjectStatsResponse(BaseModel):
    id: int
    name: str
    tasks_count: int
    done_count: int
    todo_count: int
    in_progress_count: int

    model_config = ConfigDict(from_attributes=True)


class ProjectTasksStatsResponse(BaseModel):
    name: str
    task_count: int


class ProjectWithTaskResponse(BaseModel):
    task: TaskResponse
    project: ProjectResponse
