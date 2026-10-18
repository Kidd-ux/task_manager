from fastapi import APIRouter, Depends
from db import get_db
from auth.security import get_current_user
from schemas.project import (
    ProjectResponse,
    ProjectCreate,
    ProjectUpdate,
    ProjectStatsResponse,
    ProjectTasksStatsResponse,
    ProjectWithTaskResponse,
)
from schemas.task import TaskResponse, TaskCreate
from services.project_service import (
    update_project,
    get_project,
    get_project_by_id,
    get_project_task,
    get_project_task_stats,
    create_project,
    delete_project,
    project_stat,
    create_project_with_task,
)

router = APIRouter()


@router.get("/projects/stats", response_model=list[ProjectStatsResponse])
async def project_stats(db=Depends(get_db)):
    return await project_stat(db)


@router.get("/projects", response_model=list[ProjectResponse])
async def get_pr(db=Depends(get_db)):
    return await get_project(db)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_pr_from_id(project_id: int, db=Depends(get_db)):
    res = await get_project_by_id(project_id, db)
    return res


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def get_projects_tasks(project_id: int, db=Depends(get_db)):
    res = await get_project_task(project_id, db)
    return res


@router.get("/projects/tasks/stats", response_model=list[ProjectTasksStatsResponse])
async def projects_task_stats(db=Depends(get_db)):
    return await get_project_task_stats(db)


@router.post("/projects/tasks", response_model=ProjectWithTaskResponse)
async def create_proj_task(
    project: ProjectCreate,
    task: TaskCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    return await create_project_with_task(project, task, current_user.id, db)


@router.post("/projects", response_model=ProjectResponse)
async def create_pr(
    project: ProjectCreate, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return await create_project(project, current_user.id, db)


@router.delete("/projects/{project_id}")
async def delete(
    project_id: int, current_user=Depends(get_current_user), db=Depends(get_db)
):
    res = await delete_project(project_id, current_user.id, db)
    return res


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update(
    project_id: int,
    new: ProjectUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    res = await update_project(project_id, new, current_user.id, db)
    return res
