from fastapi import APIRouter, Depends
from db import get_db
from auth.security import get_current_user
from schemas.user import (
    UserResponse,
    UserCreate,
    UserUpdate,
    UserStatsResponse,
    UserTopResponse,
)
from schemas.project import ProjectResponse
from schemas.comment import CommentResponse
from services.user_service import (
    create_user,
    update_user,
    delete_user,
    get_users,
    get_user_by_id,
    get_user_projects,
    get_user_comments,
    get_user_stat,
    get_us_top,
)

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/users/stats", response_model=list[UserStatsResponse])
async def get_users_stats(db=Depends(get_db)):
    return await get_user_stat(db)


@router.get("/users/top", response_model=list[UserTopResponse])
async def get_users_top(db=Depends(get_db)):
    return await get_us_top(db)


@router.get("/users", response_model=list[UserResponse])
async def get_all(db=Depends(get_db)):
    return await get_users(db)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_us_by_id(user_id: int, db=Depends(get_db)):
    res = await get_user_by_id(user_id, db)
    return res


@router.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
async def get_users_projects(user_id: int, db=Depends(get_db)):
    res = await get_user_projects(user_id, db)
    return res


@router.get("/users/{user_id}/comments", response_model=list[CommentResponse])
async def get_users_comments(user_id: int, db=Depends(get_db)):
    res = await get_user_comments(user_id, db)
    return res


@router.post("/users", response_model=UserResponse)
async def create(user: UserCreate, db=Depends(get_db)):
    return await create_user(user, db)


@router.patch("/users/me", response_model=UserResponse)
async def update(
    new: UserUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    res = await update_user(new, current_user.id, db)
    return res


@router.delete("/users/me")
async def delete(current_user=Depends(get_current_user), db=Depends(get_db)):
    return await delete_user(current_user.id, db)
