import json
from db import redis


async def get_projects_cache():
    return await redis.get("projects")


async def set_project_cache(data):
    value = json.dumps(
        data
    )  # ВзятьPython-объект data и превратить в JSON-текст - в "[{},{}]"
    await redis.set("projects", value, ex=60)


async def del_project_cache():
    await redis.delete("projects")
