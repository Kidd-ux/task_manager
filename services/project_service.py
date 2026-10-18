from sqlalchemy import select, func, case
from models import Project, Task
from sqlalchemy.orm import selectinload
from task_manager_exceptions import (
    ProjectNotFoundError,
    ProjectForbiddenError,
    ProjectAlreadyExistsError,
)
from sqlalchemy.exc import IntegrityError
from schemas.project import ProjectResponse
from cache.project_cache import get_projects_cache, set_project_cache, del_project_cache
from cache.task_cache import del_task_cache
from cache.comment_cache import del_comment_cache
import json


def check_project_owner(project, current_user_id):
    if project.owner_id != current_user_id:
        raise ProjectForbiddenError


async def get_project(db):

    value = await get_projects_cache()

    if value:
        data = json.loads(
            value
        )  # тут JSON-строка(value) становится листом из словарей "[{},{},{}]" --> [{},{}]
        return data

    stmt = select(Project)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalars().all()
    data = [ProjectResponse.model_validate(x).model_dump() for x in res]
    await set_project_cache(data)
    return res


async def get_project_by_id(project_id, db):
    stmt = select(Project).where(Project.id == project_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise ProjectNotFoundError
    return res


async def get_project_task(project_id, db):
    intmd_res = await db.execute(
        select(Project)
        .options(selectinload(Project.tasks))
        .where(Project.id == project_id)
    )

    proj = intmd_res.scalar_one_or_none()
    if proj is None:
        raise ProjectNotFoundError

    return proj.tasks


async def project_stat(db):
    stmt = (
        select(
            Project.id.label("id"),
            Project.name.label("name"),
            func.count(Task.id).label("tasks_count"),
            func.sum(case((Task.status == "done", 1), else_=0)).label("done_count"),
            func.sum(case((Task.status == "todo", 1), else_=0)).label("todo_count"),
            func.sum(case((Task.status == "in_progress", 1), else_=0)).label(
                "in_progress_count"
            ),
        )
        .outerjoin(Task, Project.id == Task.project_id)
        .group_by(Project.id, Project.name)
    )
    intmd_res = await db.execute(stmt)
    res = intmd_res.all()
    return res


async def get_project_task_stats(db):
    task_count = (
        select(func.count(Task.id))
        .where(Task.project_id == Project.id)
        .scalar_subquery()
    )
    stmt = select(Project.name, task_count.label("task_count"))
    intmd_res = await db.execute(stmt)
    res = intmd_res.all()
    return res


async def create_project_with_task(project, task, current_user_id, db):
    p = Project(name=project.name, owner_id=current_user_id)
    db.add(p)
    await db.flush()
    t = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        project_id=p.id,
    )
    db.add(t)
    await db.commit()
    await del_task_cache()
    await del_project_cache()
    return {"project": p, "task": t}


async def create_project(project, user_id, db):
    p = Project(name=project.name, owner_id=user_id)

    db.add(p)
    try:
        await db.commit()
        await del_project_cache()
    except IntegrityError as e:
        await db.rollback()
        if e.orig.__cause__.constraint_name == "projects_name_key":
            raise ProjectAlreadyExistsError
        raise
    return p


async def delete_project(project_id, current_user_id, db):
    stmt = select(Project).where(Project.id == project_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise ProjectNotFoundError
    check_project_owner(res, current_user_id)
    await db.delete(res)
    await db.commit()
    await del_project_cache()
    return "Project deleted"


async def update_project(project_id, new, current_user_id, db):
    stmt = select(Project).where(Project.id == project_id)
    intmd_res = await db.execute(stmt)
    proj = intmd_res.scalar_one_or_none()

    if proj is None:
        raise ProjectNotFoundError

    check_project_owner(proj, current_user_id)

    if new.name is not None:
        proj.name = new.name

    await db.commit()
    await del_project_cache()
    await del_task_cache()
    await del_comment_cache()
    return proj
