from src.redis_cache.redis_cache_manage import RedisCache

cache = RedisCache()


async def get_todos_with_cache(user_id: str, filters: dict, preload: bool = False):
    table = "todos"
    payload = {"user_id": user_id, "filters": filters}

    # If preload is True, simulate storing data manually
    if preload:
        simulated_data = {"todos": ["Task 1", "Task 2"]}
        await cache.store_payload(table=table, payload=payload, data=simulated_data, ttl=120)
        return simulated_data

    # Check if data exists in cache
    cached_data = await cache.get(table, payload)
    if cached_data is not None:
        return cached_data

    # If not found in cache
    print("🔍 No cached data found — fetching from DB...")

    async def fetch_from_db():
        # Simulate real DB logic here
        return [{"id": 1, "title": "Cached todo"}]

    # Fetch and cache the fresh data
    fresh_data = await cache.get_or_set(table, payload, fetch_from_db, ttl=60)
    return fresh_data
