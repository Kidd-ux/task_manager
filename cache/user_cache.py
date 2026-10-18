import json
from db import redis


async def get_user_cache():
    return await redis.get("users")


async def set_user_cache(data):
    value = json.dumps(data)
    await redis.set("users", value, ex=60)


async def del_user_cache():
    await redis.delete("users")
