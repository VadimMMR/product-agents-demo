from database import get_db_by_name

async def get_all_table_data(table_name: str):
    """
    (КОД 4) Переключается на нужную БД и забирает данные.
    """
    # table_name здесь выступает и как имя БД
    async with get_db_by_name(table_name) as conn:
        rows = await conn.fetch(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 100")
        return [dict(row) for row in rows]