from generator.core import AgentGenerator
import os

# Инициализируем генератор (указываем твой образ из Docker Hub)
# Замени 'your_docker_user' на свой логин
DOCKER_USER = os.getenv("DOCKERHUB_USERNAME", "your_docker_user")
generator = AgentGenerator(image_name=f"{DOCKER_USER}/product-agents-worker:latest")

async def trigger_agent_generation(agent_id: str, db_url: str):
    """
    (КОД 5) Код вызова генератора кода агента (ВГК).
    """
    # Вызываем Код №6
    config = generator.generate_config(agent_id, db_url)
    
    # В будущем здесь будет вызов API Render для запуска Job
    print(f"--- ГК сформировал конфиг для {agent_id} ---")
    return config