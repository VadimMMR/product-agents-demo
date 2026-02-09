# render_deployer.py
import os
import requests
import json
from typing import Dict, Any
import time

class RenderDeployer:
    def __init__(self):
        self.api_key = os.getenv("RENDER_API_KEY")
        self.owner_id = os.getenv("RENDER_OWNER_ID")
        self.base_url = "https://api.render.com/v1"
        
        if not self.api_key:
            raise ValueError("❌ RENDER_API_KEY не установлен")
        if not self.owner_id:
            raise ValueError("❌ RENDER_OWNER_ID не установлен")
        
        print(f"✅ RenderDeployer инициализирован. Owner: {self.owner_id[:10]}...")
    
    def create_agent_service(self, agent_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создаёт новый сервис-контейнер для агента на Render
        """
        
        # Формируем уникальное имя сервиса
        timestamp = int(time.time())
        service_name = f"agent-{agent_id}-{timestamp}"
        
        print(f"🚀 Начинаю создание сервиса: {service_name}")
        
        # Подготавливаем переменные окружения из конфига
        env_vars = []
        
        # Добавляем базовые переменные
        base_vars = {
            "AGENT_ID": agent_id,
            "PYTHONUNBUFFERED": "1"
        }
        
        # Объединяем с переменными из конфига
        if "environment" in agent_config:
            for key, value in agent_config["environment"].items():
                base_vars[key] = str(value)
        
        # Конвертируем в формат Render API
        for key, value in base_vars.items():
            env_vars.append({"key": key, "value": value})
        
        # Формируем payload для API
        payload = {
            "autoDeploy": "no",
            "branch": None,
            "name": service_name,
            "ownerId": self.owner_id,
            "repo": None,
            "serviceDetails": {
                "env": "docker",
                "envSpecificDetails": {
                    "dockerCommand": "",
                    "dockerContext": ".",
                    "dockerfilePath": None,
                    "registryCredentialId": None,
                    "image": {
                        "ownerId": self.owner_id,
                        "imagePath": agent_config.get("image", os.getenv("DOCKER_IMAGE", "dayg0555/product-agents-worker:latest")),
                        "registryCredentialId": None
                    }
                },
                "envVars": env_vars,
                "healthCheckPath": "/health",
                "numInstances": 1,
                "plan": "free",  # Используем бесплатный план
                "pullRequestPreviewsEnabled": "no",
                "region": "oregon",
                "startCommand": agent_config.get("command", "python run_worker.py")
            },
            "type": "web_service"
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"📦 Отправляю запрос в Render API...")
        print(f"   Образ: {payload['serviceDetails']['envSpecificDetails']['image']['imagePath']}")
        print(f"   Переменные: {[e['key'] for e in env_vars]}")
        
        try:
            response = requests.post(
                f"{self.base_url}/services",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"📥 Ответ API: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                service_data = result.get("service", {})
                
                print(f"✅ Сервис создан успешно!")
                print(f"   ID: {service_data.get('id')}")
                print(f"   Имя: {service_data.get('slug')}")
                print(f"   URL: {service_data.get('serviceDetails', {}).get('url', 'N/A')}")
                
                return {
                    "success": True,
                    "service_id": service_data.get("id"),
                    "service_name": service_data.get("slug"),
                    "dashboard_url": service_data.get("dashboardUrl"),
                    "service_url": service_data.get("serviceDetails", {}).get("url"),
                    "status": "created"
                }
            else:
                error_text = response.text[:500] if len(response.text) > 500 else response.text
                print(f"❌ Ошибка API: {response.status_code}")
                print(f"   Подробности: {error_text}")
                
                return {
                    "success": False,
                    "error": f"API вернул {response.status_code}",
                    "details": error_text
                }
                
        except requests.exceptions.Timeout:
            print("❌ Таймаут при подключении к Render API")
            return {"success": False, "error": "Timeout connecting to Render API"}
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_connection(self):
        """Тестирует подключение к Render API"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = requests.get(
                f"{self.base_url}/services",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                services = response.json()
                print(f"✅ Подключение к Render API успешно!")
                print(f"   Найдено сервисов: {len(services)}")
                return True
            else:
                print(f"❌ Ошибка подключения: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

# Функция для быстрого теста
def test_deployer():
    """Быстрый тест деплоера"""
    print("🧪 Тестируем RenderDeployer...")
    
    try:
        deployer = RenderDeployer()
        
        # Тестируем подключение
        if not deployer.test_connection():
            return
        
        # Тестовый конфиг
        test_config = {
            "image": "dayg0555/product-agents-worker:latest",
            "environment": {
                "AGENT_ID": "test-001",
                "URL_AGENTS": "postgresql://...",
                "URL_FRUITS": "postgresql://...",
                "URL_VEGETABLES": "postgresql://...",
                "URL_FISH": "postgresql://..."
            },
            "command": "python run_worker.py"
        }
        
        print("\n🚀 Пробуем создать тестовый сервис...")
        result = deployer.create_agent_service("test-001", test_config)
        
        print("\n📊 Результат:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ Ошибка при тесте: {e}")

if __name__ == "__main__":
    test_deployer()