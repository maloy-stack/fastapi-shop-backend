"""import redis.asyncio as aioredis"""
import redis.asyncio as aioredis
from app.config import REDIS_URL

LUA_DECREMENT_SCRIPT = """
local key = KEYS[1]
local decrement_by = tonumber(ARGV[1])
local current = redis.call('GET', key)
if current == false then
    return -1  -- товара нет в кэше
end
current = tonumber(current)
if current >= decrement_by then
    redis.call('DECRBY', key, decrement_by)
    return 1   -- успех
else
    return 0   -- недостаточно stock
end
"""

class RedisClient:
    def __init__(self, url: str):
        self._url = url
        self._redis = aioredis.from_url(url, decode_responses=True)
        self._script_sha = None

    async def initialize(self):
        self._script_sha = await self._redis.script_load(LUA_DECREMENT_SCRIPT)

    async def decrement_stock(self, product_id: int, amount: int) -> int:
        key = f"product_stock:{product_id}"
        return int(await self._redis.evalsha(self._script_sha, 1, key, amount))

    @property
    def client(self):
        return self._redis

redis_client = RedisClient(REDIS_URL)