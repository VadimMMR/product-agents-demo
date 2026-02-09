import os
import sys
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from .vgk_handler import trigger_agent_generation
from .data_service import get_all_table_data

sys.path.append("..")
from database import get_db_by_name
from render_deployer import RenderDeployer

async def create_agent_logic(agent_id: str, parse_link: str):
    db_url = os.getenv("URL_AGENTS")
    
    # 1. Сохраняем агента в БД
    async with get_db_by_name("agents") as conn:
        await conn.execute(
            "INSERT INTO agents (num_agents, parse_link) VALUES ($1, $2) "
            "ON CONFLICT (num_agents) DO UPDATE SET parse_link = $2",
            agent_id, parse_link
        )
    
    # 2. Генерируем конфиг
    from .vgk_handler import trigger_agent_generation
    config = await trigger_agent_generation(agent_id, db_url)
    
    # 3. Добавляем команду запуска
    config["command"] = "python run_worker.py"
    
    # 4. Создаём сервис на Render
    print(f"🎯 Создаю контейнер для агента {agent_id} на Render...")
    deployer = RenderDeployer()
    deployment_result = deployer.create_agent_service(agent_id, config)
    
    # 5. Сохраняем информацию о деплое
    if deployment_result.get("success"):
        async with get_db_by_name("agents") as conn:
            await conn.execute(
                """
                UPDATE agents 
                SET render_service_id = $1, 
                    render_service_name = $2,
                    deployed_at = CURRENT_TIMESTAMP
                WHERE num_agents = $3
                """,
                deployment_result.get("service_id"),
                deployment_result.get("service_name"),
                agent_id
            )
    
    # 6. Возвращаем результат
    response_data = {
        "agent_id": agent_id,
        "config": config,
        "deployment": deployment_result
    }
    
    if deployment_result.get("success"):
        response_data.update({
            "status": "success",
            "message": f"✅ Агент {agent_id} создан. Контейнер запускается на Render.",
            "dashboard_url": deployment_result.get("dashboard_url")
        })
    else:
        response_data.update({
            "status": "partial_success",
            "message": f"⚠️ Агент создан, но контейнер не запущен: {deployment_result.get('error')}",
            "note": "Агент сохранён в БД, но требуется ручной запуск контейнера"
        })
    
    return response_data

async def get_table_data_logic(table_name: str):
    data = await get_all_table_data(table_name)
    return {"table": table_name, "rows": data}

def serve_frontend_logic():
    path = "/app/frontend/index.html"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
