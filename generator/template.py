def get_agent_env_template(agent_id: str, db_url: str):
    """
    (КОД 7) Шаблон конфигурации. 
    Определяет, с какими переменными запустится универсальный воркер.
    """
    return {
        "AGENT_ID": agent_id,
        "DATABASE_URL": db_url,
        "PYTHONUNBUFFERED": "1"
    }