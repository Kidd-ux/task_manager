from sqlalchemy import select
from models import Comment, Task
from sqlalchemy.orm import selectinload
from task_manager_exceptions import (
    CommentNotFoundError,
    TaskNotFoundError,
    CommentForbiddenError,
)
import json
from schemas.comment import CommentResponse
from cache.comment_cache import get_comment_cache, set_comment_cache, del_comment_cache


async def get_comments(db):

    value = await get_comment_cache()

    if value:
        data = json.loads(value)  # снова сделали pyhton объекты
        return data

    intmd_res = await db.execute(select(Comment))
    res = intmd_res.scalars().all()
    data = [CommentResponse.model_validate(x).model_dump() for x in res]
    await set_comment_cache(data)
    return res


async def get_comment_by_id(com_id, db):
    stmt = select(Comment).where(Comment.id == com_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise CommentNotFoundError
    return res


async def create_comment(com, current_user_id, db):
    stmt = (
        select(Task).options(selectinload(Task.project)).where(Task.id == com.task_id)
    )
    intmd_res = await db.execute(stmt)
    task = intmd_res.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError

    if task.project.owner_id != current_user_id:
        raise CommentForbiddenError

    c = Comment(text=com.text, task_id=com.task_id, user_id=current_user_id)
    db.add(c)
    await db.commit()
    await del_comment_cache()
    return c


async def update_comment(com_id, new, current_user_id, db):
    stmt = select(Comment).where(Comment.id == com_id)
    intmd_res = await db.execute(stmt)
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise CommentNotFoundError

    if res.user_id != current_user_id:
        raise CommentForbiddenError

    if new.text is not None:
        res.text = new.text

    await db.commit()
    await del_comment_cache()
    return res


async def delete_comment(com_id, current_user_id, db):
    intmd_res = await db.execute(select(Comment).where(Comment.id == com_id))
    res = intmd_res.scalar_one_or_none()
    if res is None:
        raise CommentNotFoundError

    if res.user_id != current_user_id:
        raise CommentForbiddenError

    await db.delete(res)
    await db.commit()
    await del_comment_cache()
    return "Comment has been deleted"
