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
DATABASE_URL = os.getenv("DATABASE_URL")
AGENT_ID = os.getenv("AGENT_ID") # Название или ID агента

async def get_config():
    """Получаем ссылку для парсинга из БД Neon (Исправлено: используем курсор)"""
    try:
        async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
            async with conn.cursor() as cur:
                # В твоей базе колонка называется num_agents
                await cur.execute(
                    "SELECT parse_link FROM agents WHERE num_agents = %s",
                    (AGENT_ID,)
                )
                row = await cur.fetchone()
                return row[0] if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении конфигурации: {e}")
        return None

async def save_result(table_name, column_name, product_name):
    """Сохранение данных (Исправлено: добавлен курсор и транзакции)"""
    try:
        async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
            async with conn.cursor() as cur:
                # 1. Создаем таблицу, если нет (Self-healing)
                await cur.execute(sql.SQL("""
                    CREATE TABLE IF NOT EXISTS {} (
                        id BIGSERIAL PRIMARY KEY,
                        {} TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """).format(sql.Identifier(table_name), sql.Identifier(column_name)))
                
                # 2. Вставляем данные (ON CONFLICT предотвращает дубли)
                await cur.execute(sql.SQL("""
                    INSERT INTO {} ({}) VALUES (%s)
                    ON CONFLICT ({}) DO NOTHING
                """).format(
                    sql.Identifier(table_name), 
                    sql.Identifier(column_name),
                    sql.Identifier(column_name)
                ), (product_name,))
                
                await conn.commit()
                logger.info(f"✅ Сохранено: {product_name} в {table_name}")
    except Exception as e:
        logger.error(f"ОШИБКА сохранения в БД: {e}")

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
    """Основной цикл (Исправлено: логика сопоставления)"""
    if not AGENT_ID or not DATABASE_URL:
        logger.error("Критическая ошибка: Не заданы AGENT_ID или DATABASE_URL")
        return

    logger.info(f"🚀 Воркер {AGENT_ID} начал работу")
    
    parse_url = await get_config()
    if not parse_url:
        logger.warning(f"Задание для агента {AGENT_ID} не найдено в базе данных")
        return

    # Категории поиска (можно позже тоже вынести в БД)
    categories = {
        "fruits": ["Яблоко", "Банан", "Апельсин", "Груша"],
        "vegetables": ["Картофель", "Морковь", "Помидор"],
        "fish": ["Лосось", "Тунец"]
    }
    
    for category, terms in categories.items():
        logger.info(f"🔎 Поиск {category} на {parse_url}...")
        found_items = parse_page(parse_url, terms)
        
        for item in found_items:
            await save_result(category, category, item)

    logger.info(f"🏁 Воркер {AGENT_ID} завершил задачу")

if __name__ == "__main__":
    asyncio.run(run_worker())