from fastapi import APIRouter, Depends, Query
from db import get_db
from auth.security import get_current_user
from schemas.task import TaskResponse, TaskCreate, TaskUpdate
from schemas.comment import CommentResponse
from typing import Literal
from services.task_service import (
    create_task,
    update_task,
    delete_task,
    get_tasks,
    get_task_by_id,
    get_task_comments,
    get_user_tasks,
)

router = APIRouter()


@router.get("/tasks", response_model=list[TaskResponse])
async def get_all_task(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order: Literal["desc", "asc"] = "desc",
    sort: Literal["id", "title"] | None = None,
    search: str | None = Query(None, min_length=1, max_length=100),
    project_id: int | None = Query(None, ge=1),
    status: Literal["todo", "in_progress", "done"] | None = None,
    db=Depends(get_db),
):
    return await get_tasks(db, status, project_id, search, sort, order, limit, offset)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db=Depends(get_db)):
    res = await get_task_by_id(task_id, db)
    return res


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_tasks_comments(task_id: int, db=Depends(get_db)):
    res = await get_task_comments(task_id, db)
    return res


@router.get("/tasks/by-user/{user_id}", response_model=list[TaskResponse])
async def get_users_tasks(user_id: int, db=Depends(get_db)):
    res = await get_user_tasks(user_id, db)
    return res


@router.post("/tasks", response_model=TaskResponse)
async def create(
    task: TaskCreate, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return await create_task(task, current_user.id, db)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update(
    task_id: int,
    new: TaskUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    res = await update_task(task_id, new, current_user.id, db)
    return res


@router.delete("/tasks/{task_id}")
async def delete(
    task_id: int, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return await delete_task(task_id, current_user.id, db)
