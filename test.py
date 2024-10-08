import asyncpg
import asyncio
async def test_connection():
    conn = await asyncpg.connect(
        user='coder',
        password='eeS30AfQ2OrczWUTCMTFL23GDjK1urwN',
        database='coderdb_ljno',
        host='dpg-crhdn8dsvqrc738c7pt0-a',
        port=5432,
    )
    await conn.close()

asyncio.run(test_connection())
