from sqlalchemy import select, func
from models import User, Project, Comment
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from task_manager_exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UserHasRelationsError,
)
from auth.security import hash_password
import json
from cache.user_cache import get_user_cache, set_user_cache, del_user_cache
from schemas.user import UserResponse


async def get_users(db):
    value = await get_user_cache()
    if value:
        data = json.loads(value)
        return data

    intmd_res = await db.execute(select(User))
    res = intmd_res.scalars().all()
    data = [UserResponse.model_validate(x).model_dump() for x in res]
    await set_user_cache(data)
    return res


async def get_user_by_id(user_id, db):
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    res = result.scalar_one_or_none()
    if res is None:
        raise UserNotFoundError
    return res


async def get_user_projects(user_id, db):
    res = await db.execute(
        select(User).options(selectinload(User.projects)).where(User.id == user_id)
    )
    user = res.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError
    return user.projects


async def get_user_comments(user_id, db):
    res = await db.execute(
        select(User).options(selectinload(User.comments)).where(User.id == user_id)
    )
    user = res.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError

    return user.comments


async def get_user_stat(db):
    stmt = (
        select(
            User.id.label("id"),
            User.username.label("username"),
            func.count(Project.id.distinct()).label("projects_count"),
            func.count(Comment.id.distinct()).label("comments_count"),
        )
        .outerjoin(Project, Project.owner_id == User.id)
        .outerjoin(Comment, Comment.user_id == User.id)
        .group_by(User.id, User.username)
    )

    interim_res = await db.execute(stmt)
    res = interim_res.all()
    return res


async def get_us_top(db):
    subq = (
        select(User.username, func.count(Comment.id).label("comment_count"))
        .join(Comment, Comment.user_id == User.id)
        .group_by(User.id, User.username)
    )  # сейчас эта переменная держит в себе имя и кол-во комметариев написанных этим именем типа Олег 5, Аня 6 и тд
    subq = subq.subquery()

    avg = select(
        func.avg(subq.c.comment_count)
    ).scalar_subquery()  # тут переменная это число котороя является ср значением колва комментариев, число благодаря scalar_subquery()

    stmt = select(subq.c.username, subq.c.comment_count).where(
        subq.c.comment_count > avg
    )  # выполняем запрос выведи из subq имя, и из subq кол-во комментариев для каждого человека у которого оно больше ср значения кол-ва комментариев
    interim_res = await db.execute(stmt)
    res = interim_res.all()
    return res


async def create_user(user, db):
    hashed = hash_password(user.password)
    u = User(
        username=user.username, email=user.email, age=user.age, password_hash=hashed
    )
    try:
        db.add(u)
        await db.commit()
        await del_user_cache()
        return u
    except IntegrityError as e:
        await db.rollback()
        if e.orig.__cause__.constraint_name == "users_email_key":
            raise EmailAlreadyExistsError
        raise


async def update_user(new, current_user_id, db):
    stmt = select(User).where(User.id == current_user_id)
    interim_res = await db.execute(stmt)

    res = interim_res.scalar_one_or_none()
    if res is None:
        raise UserNotFoundError

    if new.username is not None:
        res.username = new.username
    if new.email is not None:
        res.email = new.email
    if new.age is not None:
        res.age = new.age
    try:
        await db.commit()
        await del_user_cache()
        return res
    except IntegrityError as e:
        await db.rollback()
        if e.orig.__cause__.constraint_name == "users_email_key":
            raise EmailAlreadyExistsError
        raise


async def delete_user(current_user_id, db):
    interim_res = await db.execute(select(User).where(User.id == current_user_id))

    res = interim_res.scalar_one_or_none()

    if res is None:
        raise UserNotFoundError
    interim_project_exists = await db.execute(
        select(Project).where(Project.owner_id == current_user_id).limit(1)
    )
    project_exists = interim_project_exists.first()

    interim_comment_exists = await db.execute(
        select(Comment).where(Comment.user_id == current_user_id).limit(1)
    )
    comment_exists = interim_comment_exists.first()

    if project_exists or comment_exists:
        raise UserHasRelationsError

    await db.delete(res)
    await db.commit()
    await del_user_cache()
    return "User has been deleted"


# change in test branch
