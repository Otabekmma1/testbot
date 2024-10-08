import asyncpg
import asyncio
async def test_connection():
    conn = await asyncpg.connect(
        user='coder',
        password='eeS30AfQ2OrczWUTCMTFL23GDjK1urwN',
        database='coderdb_ljno',
        host='localhost',
        port=5432,
    )
    await conn.close()

asyncio.run(test_connection())
