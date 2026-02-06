from fastapi import APIRouter, Request
from services.agent_service import create_agent_logic, get_table_data_logic, serve_frontend_logic

router = APIRouter()

@router.get("/")
async def home(request: Request):
    return serve_frontend_logic()

@router.post("/api/agents/create")
async def create_agent_api(agent_id: str, parse_link: str):
    return await create_agent_logic(agent_id, parse_link)

@router.get("/api/data/{table_name}")
async def get_data_api(table_name: str):
    return await get_table_data_logic(table_name)