from pydantic import BaseModel, ConfigDict, Field


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str
    email: str
    age: int = Field(ge=1)
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    age: int | None = Field(None, ge=1)


class UserStatsResponse(BaseModel):
    id: int
    username: str
    projects_count: int
    comments_count: int

    model_config = ConfigDict(from_attributes=True)


class UserTopResponse(BaseModel):
    username: str
    comment_count: int
