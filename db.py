import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis.asyncio import Redis

# from config import DATABASE_URL, REDIS_HOST, REDIS_PORT
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:password@127.0.0.1:5432/task_manager"
)
REDIS_DB = os.getenv("REDIS_DB", 0)
engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

redis = Redis(host="127.0.0.1", port=6379, decode_responses=True, db=int(REDIS_DB))


async def get_db():
    async with SessionLocal() as db:
        yield db


class Base(DeclarativeBase):
    pass
