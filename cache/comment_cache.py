import json
from db import redis


async def get_comment_cache():
    return await redis.get("comments")


async def set_comment_cache(data):
    value = json.dumps(data)  # сделали json строку и положили в value
    await redis.set("comments", value, ex=60)


async def del_comment_cache():
    await redis.delete("comments")
