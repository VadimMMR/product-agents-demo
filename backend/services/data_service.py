from database import get_async_db

async def get_all_table_data(table_name: str):
    """
    (КОД 4) Код получения данных.
    Безопасно читает данные из указанной таблицы.
    """
    allowed_tables = ["fruits", "vegetables", "fish", "agents"]
    if table_name not in allowed_tables:
        return []

    async with get_async_db() as conn:
        # Используем fetch для получения списка строк
        rows = await conn.fetch(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 100")
        # Конвертируем записи в обычные словари для JSON
        return [dict(row) for row in rows]