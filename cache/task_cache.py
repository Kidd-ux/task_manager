import json
from db import redis


async def get_task_cache(key):
    return await redis.get(key)


async def set_task_cache(data, key):
    value = json.dumps(data)
    await redis.set(key, value, ex=60)


async def del_task_cache():
    cursor = 0
    while True:

        cursor, keys = await redis.scan(cursor=cursor, match="tasks:*")
        if keys:
            await redis.delete(*keys)
        if cursor == 0:
            break
