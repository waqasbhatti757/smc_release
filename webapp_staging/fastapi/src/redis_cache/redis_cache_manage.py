import json
import hashlib
from typing import Any, Optional, Callable
import redis.asyncio as redis
from pydantic import BaseModel


class RedisCache:
    def __init__(self, host="localhost", port=6379, db=0, default_ttl=300):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = default_ttl

    def _make_cache_key(self, table: str, payload: Any) -> str:
        """
        Generate a unique Redis key using table name + hashed payload.
        """
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        return f"{table}:{payload_hash}"

    async def get(self, table: str, payload: Any) -> Optional[Any]:
        key = self._make_cache_key(table, payload)
        result = await self.client.get(key)
        return json.loads(result) if result else None

    async def set(self, table: str, payload: Any, data: Any, ttl: Optional[int] = None) -> None:
        key = self._make_cache_key(table, payload)
        value = json.dumps(data, default=str)
        await self.client.set(key, value, ex=ttl or self.default_ttl)

    async def get_or_set(
        self,
        table: str,
        payload: Any,
        data_func: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        Returns cached value if present. Otherwise computes using `data_func`, saves, and returns it.
        """
        cached = await self.get(table, payload)
        if cached is not None:
            return cached

        data = await data_func() if callable(data_func) else data_func
        await self.set(table, payload, data, ttl)
        return data

    async def store_payload(
        self,
        table: str,
        payload: Any,
        data: Any,
        ttl: Optional[int] = None
    ) -> str:
        """
        Directly stores a payload and data in Redis with optional TTL.
        Returns the generated cache key for reference.
        """
        key = self._make_cache_key(table, payload)
        value = json.dumps(data, default=str)
        await self.client.set(key, value, ex=ttl or self.default_ttl)
        return key
