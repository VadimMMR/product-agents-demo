import os
import asyncio
import psycopg
from psycopg import sql
from bs4 import BeautifulSoup
import requests
import logging

# Настройка логов, чтобы видеть прогресс в Docker/Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Данные из окружения
URLS = {
    "agents": os.getenv("URL_AGENTS"),
    "fruits": os.getenv("URL_FRUITS"),
    "vegetables": os.getenv("URL_VEGETABLES"),
    "fish": os.getenv("URL_FISH")
}
AGENT_ID = os.getenv("AGENT_ID") # Название или ID агента

async def get_config():
    """Получаем ссылку для парсинга из БД Neon"""
    try:
        db_url = URLS.get("agents")
        async with await psycopg.AsyncConnection.connect(db_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT parse_link FROM agents WHERE num_agents = %s",
                    (AGENT_ID,)
                )
                row = await cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении конфигурации: {e}")
        return None

async def save_result(db_key, product_name):
    """db_key может быть 'fruits', 'vegetables' или 'fish'"""
    db_url = URLS.get(db_key)
    if not db_url:
        logger.error(f"❌ Не найден URL для базы данных: {db_key}")
        return
    
    try:
        async with await psycopg.AsyncConnection.connect(db_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql.SQL("INSERT INTO {} ({}) VALUES (%s) ON CONFLICT DO NOTHING")
                    .format(sql.Identifier(db_key), sql.Identifier(db_key)), (product_name,))
                await conn.commit()
                logger.info(f"✅ Сохранено: {product_name} в таблицу {db_key}")
    except Exception as e:
        logger.error(f"ОШИБКА сохранения в БД {db_key}: {e}")

def parse_page(url, search_terms):
    """Реальная логика парсинга (Исправлено: добавлена из твоей старой версии)"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        found = [term for term in search_terms if term.lower() in page_text]
        return list(set(found)) # Только уникальные находки
    except Exception as e:
        logger.error(f"Ошибка парсинга страницы {url}: {e}")
        return []

async def run_worker():
    """Основной цикл"""
    if not AGENT_ID or not URLS.get("agents"):
        logger.error("Критическая ошибка: Не заданы AGENT_ID или URL_AGENTS")
        return

    logger.info(f"🚀 Воркер {AGENT_ID} начал работу")
    
    parse_url = await get_config()
    if not parse_url:
        logger.warning(f"Задание для агента {AGENT_ID} не найдено в базе данных")
        return

    categories = {
        "fruits": ["Яблоко", "Банан", "Апельсин", "Груша"],
        "vegetables": ["Картофель", "Морковь", "Помидор"],
        "fish": ["Лосось", "Тунец"]
    }
    
    for category, terms in categories.items():
        logger.info(f"🔎 Поиск {category} на {parse_url}...")
        found_items = parse_page(parse_url, terms)
        
        for item in found_items:
            await save_result(category, item)  # Измененный вызов

    logger.info(f"🏁 Воркер {AGENT_ID} завершил задачу")

if __name__ == "__main__":
    asyncio.run(run_worker())