from sqlalchemy import select
from models import Task, Comment, Project, User
from sqlalchemy.orm import selectinload
from task_manager_exceptions import (
    UserNotFoundError,
    TaskNotFoundError,
    ProjectNotFoundError,
    TaskForbiddenError,
)
import json
from schemas.task import TaskResponse
from cache.task_cache import get_task_cache, set_task_cache, del_task_cache
from cache.comment_cache import del_comment_cache


def check_task_owner(task, current_user_id):
    if task.project.owner_id != current_user_id:
        raise TaskForbiddenError


async def get_tasks(db, status, project_id, search, sort, order, limit, offset):
    key = f"tasks:{status}:{project_id}:{search}:{sort}:{order}:{limit}:{offset}"
    value = await get_task_cache(key)

    if value:
        data = json.loads(value)
        return data

    stmt = select(Task)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if project_id is not None:
        stmt = stmt.where(Task.project_id == project_id)
    if search is not None:
        stmt = stmt.where(Task.title.ilike(f"%{search}%"))
    if sort == "id":
        if order == "desc":
            stmt = stmt.order_by(Task.id.desc())
        else:
            stmt = stmt.order_by(Task.id.asc())
    if sort == "title":
        if order == "desc":
            stmt = stmt.order_by(Task.title.desc())
        else:
            stmt = stmt.order_by(Task.title.asc())
    stmt = stmt.limit(limit)
    stmt = stmt.offset(offset)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalars().all()
    data = [TaskResponse.model_validate(x).model_dump() for x in res]
    await set_task_cache(data, key)
    return res


async def get_user_tasks(user_id, db):
    intmd_res = await db.execute(select(User).where(User.id == user_id))
    user = intmd_res.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError
    stmt = (
        select(Task)
        .join(Project, Task.project_id == Project.id)
        .where(Project.owner_id == user_id)
    )
    intmd_res2 = await db.execute(stmt)
    res = intmd_res2.scalars().all()
    return res


async def get_task_by_id(task_id, db):
    stmt = select(Task).where(Task.id == task_id)
    intmd_res = await db.execute(stmt)
    task = intmd_res.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError
    return task


async def get_task_comments(task_id, db):
    intmd_res = await db.execute(
        select(Task).options(selectinload(Task.comments)).where(Task.id == task_id)
    )
    task = intmd_res.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError

    return task.comments


async def create_task(task, current_user_id, db):
    stmt = select(Project).where(Project.id == task.project_id)
    intmd_res = await db.execute(stmt)
    project = intmd_res.scalar_one_or_none()

    if project is None:
        raise ProjectNotFoundError

    if project.owner_id != current_user_id:
        raise TaskForbiddenError

    t = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=task.project_id,
    )
    db.add(t)
    await db.commit()
    await del_task_cache()
    return t


async def update_task(task_id, new, current_user_id, db):
    stmt = select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise TaskNotFoundError
    check_task_owner(res, current_user_id)

    if new.title is not None:
        res.title = new.title
    if new.description is not None:
        res.description = new.description
    if new.status is not None:
        res.status = new.status
    await db.commit()
    await del_task_cache()
    return res


async def delete_task(task_id, current_user_id, db):
    stmt = select(Task).options(selectinload(Task.project)).where(Task.id == task_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise TaskNotFoundError
    check_task_owner(res, current_user_id)
    await db.delete(res)
    await db.commit()
    await del_task_cache()
    await del_comment_cache()
    return "Task Deleted"
