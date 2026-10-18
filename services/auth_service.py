from sqlalchemy import select
from models import User
from task_manager_exceptions import UserNotFoundError, InvalidCredentialsError
from auth.security import verify_password, create_access_token


async def login_service(data, db):
    stmt = select(User).where(User.email == data.email)
    intmd_user = await db.execute(stmt)
    user = intmd_user.scalar_one_or_none()
    if user is None:
        raise InvalidCredentialsError
    if not verify_password(data.password, user.password_hash):
        raise InvalidCredentialsError
    return create_access_token(user.id)
