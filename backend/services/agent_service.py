import os
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from .vgk_handler import trigger_agent_generation
from .data_service import get_all_table_data
import sys
sys.path.append("..")
from database import get_async_db

async def create_agent_logic(agent_id: str, parse_link: str):
    db_url = os.getenv("DATABASE_URL")
    async with get_async_db() as conn:
        await conn.execute(
            "INSERT INTO agents (num_agents, parse_link) VALUES ($1, $2) "
            "ON CONFLICT (num_agents) DO UPDATE SET parse_link = $2",
            agent_id, parse_link
        )
    config = await trigger_agent_generation(agent_id, db_url)
    return {"status": "success", "config": config}

async def get_table_data_logic(table_name: str):
    data = await get_all_table_data(table_name)
    return {"table": table_name, "rows": data}

def serve_frontend_logic():
    path = os.path.join(os.path.dirname(__file__), "../../frontend/index.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())