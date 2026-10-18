import jwt
import os
from fastapi import Depends
from db import get_db
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

# from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from models import User
from task_manager_exceptions import InvalidCredentialsError, InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY is not set")
ALGORITHM = "HS256"


password_hash = PasswordHash.recommended()


async def get_current_user(  # Функция возвращения текущего пользователя, именно ORM модели
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise InvalidTokenError

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenError
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise InvalidTokenError

    stmt = select(User).where(User.id == user_id)
    intmd_user = await db.execute(stmt)
    user = intmd_user.scalar_one_or_none()
    if user is None:
        raise InvalidCredentialsError
    return user


def create_access_token(
    user_id: int,
):  # принимает user_id из post auth # Функция создания и подписания токена
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)  # время действия токена
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }  # пейлоад - информация о пользователе и окончании токена

    return jwt.encode(
        payload, SECRET_KEY, algorithm=ALGORITHM
    )  # подпиши токен, используя информацию о пользователе и окончании токена, с помощью секретного ключа и алгоритма


def hash_password(password: str) -> str:  # функция хэширования пароля
    return password_hash.hash(password)


def verify_password(
    password: str, hashed: str
) -> bool:  # Функция проверки пароля( сравнивает пароль и хэш из бд)
    return password_hash.verify(password, hashed)
