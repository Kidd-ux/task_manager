from pydantic import BaseModel, ConfigDict


class CommentResponse(BaseModel):
    id: int
    text: str
    task_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    text: str
    task_id: int


class CommentUpdate(BaseModel):
    text: str
