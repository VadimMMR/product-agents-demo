# backend/database.py
import os
import asyncpg
from contextlib import asynccontextmanager

# Словарь со всеми URL
DB_URLS = {
    "agents": os.getenv("URL_AGENTS"),
    "fruits": os.getenv("URL_FRUITS"),
    "vegetables": os.getenv("URL_VEGETABLES"),
    "fish": os.getenv("URL_FISH")
}

_pools = {}

async def get_pool(db_name: str):
    global _pools
    if db_name not in _pools:
        url = DB_URLS.get(db_name)
        if not url:
            raise ValueError(f"URL для базы {db_name} не найден!")
        _pools[db_name] = await asyncpg.create_pool(url, ssl="require")
    return _pools[db_name]

@asynccontextmanager
async def get_db_by_name(db_name: str):
    pool = await get_pool(db_name)
    async with pool.acquire() as conn:
        yield conn
