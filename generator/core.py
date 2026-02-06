from .template import get_agent_env_template
import os

class AgentGenerator:
    def __init__(self, image_name: str):
        self.image_name = image_name

    def generate_config(self, agent_id: str):
        # Собираем все ссылки из окружения Бэкенда
        all_urls = {
            "URL_AGENTS": os.getenv("URL_AGENTS"),
            "URL_FRUITS": os.getenv("URL_FRUITS"),
            "URL_VEGETABLES": os.getenv("URL_VEGETABLES"),
            "URL_FISH": os.getenv("URL_FISH")
        }
        
        # Передаем их в шаблон (Код №7)
        # Мы немного расширим шаблон, чтобы он принимал словарь ссылок
        env_vars = {
            "AGENT_ID": agent_id,
            **all_urls # Распаковываем все ссылки в переменные контейнера
        }
        
        return {
            "image": self.image_name,
            "environment": env_vars
        }