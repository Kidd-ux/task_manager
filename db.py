from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker
from redis.asyncio import Redis

from config import DATABASE_URL, REDIS_HOST, REDIS_PORT, REDIS_DB

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

redis = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, db=int(REDIS_DB))


async def get_db():
    async with SessionLocal() as db:
        yield db


class Base(DeclarativeBase):
    pass
