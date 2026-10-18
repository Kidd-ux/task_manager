from fastapi import APIRouter, Depends
from db import get_db
from auth.security import get_current_user
from schemas.comment import CommentResponse, CommentCreate, CommentUpdate
from services.comment_service import (
    create_comment,
    update_comment,
    delete_comment,
    get_comments,
    get_comment_by_id,
)

router = APIRouter()


@router.get("/comments", response_model=list[CommentResponse])
async def get_all(db=Depends(get_db)):
    return await get_comments(db)


@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_com_by_id(comment_id: int, db=Depends(get_db)):
    res = await get_comment_by_id(comment_id, db)
    return res


@router.post("/comments", response_model=CommentResponse)
async def create(
    com: CommentCreate, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return await create_comment(com, current_user.id, db)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update(
    comment_id: int,
    new: CommentUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    res = await update_comment(comment_id, new, current_user.id, db)
    return res


@router.delete("/comments/{comment_id}")
async def delete(
    comment_id: int, current_user=Depends(get_current_user), db=Depends(get_db)
):
    return await delete_comment(comment_id, current_user.id, db)
