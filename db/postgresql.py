import asyncio
import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
import config
from typing import Union, List, Dict, Any


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command: str, *args: Any,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False,
                      executemany: bool = False):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                if fetch:
                    return await connection.fetch(command, *args)
                elif fetchval:
                    return await connection.fetchval(command, *args)
                elif fetchrow:
                    return await connection.fetchrow(command, *args)
                elif execute:
                    return await connection.execute(command, *args)
                elif executemany:
                    return await connection.executemany(command, [*args])

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS "User" (
        id BIGSERIAL PRIMARY KEY,
        telegram_id BIGINT NOT NULL UNIQUE,
        username VARCHAR(255) DEFAULT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_movies(self):
        sql = """
        CREATE TABLE IF NOT EXISTS "Movie" (
        id BIGSERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        year INT NOT NULL,
        genre VARCHAR(255) NOT NULL,
        language VARCHAR(255) NOT NULL,
        code VARCHAR(255) NOT NULL,
        video_file_id VARCHAR(255) DEFAULT NULL
        );
        """
        await self.execute(sql, execute=True)


    async def create_table_channels(self):
        sql = """
        CREATE TABLE IF NOT EXISTS "Channel" (
        channel_id VARCHAR(100) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url TEXT DEFAULT NULL
        );
        """
        await self.execute(sql, execute=True)

    # Foydalanuvchilarni olish
    async def select_all_users(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM \"User\";"
        return await self.execute(sql, fetch=True)

    # Kanallarni olish
    async def select_all_channels(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM \"Channel\";"
        return await self.execute(sql, fetch=True)

    # Filmlarni olish
    async def select_all_movies(self) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM \"Movie\";"
        return await self.execute(sql, fetch=True)

    # Foydalanuvchini qo'shish
    async def add_user(self, telegram_id: int, username: str) -> None:
        sql = "INSERT INTO \"User\" (telegram_id, username) VALUES ($1, $2);"
        await self.execute(sql, telegram_id, username, execute=True)

    # Kanal qo'shish
    async def add_channel(self, channel_id: str, name: str, url: str) -> None:
        sql = "INSERT INTO \"Channel\" (channel_id, name, url) VALUES ($1, $2, $3);"
        await self.execute(sql, channel_id, name, url, execute=True)

    # Film qo'shish
    async def add_movie(self, title: str, year: int, genre: str, language: str, code: str, video_file_id: str) -> None:
        sql = "INSERT INTO \"Movie\" (title, year, genre, language, code, video_file_id) VALUES ($1, $2, $3, $4, $5, $6);"
        await self.execute(sql, title, year, genre,language, code, video_file_id, execute=True)

    # Foydalanuvchini o'chirish
    async def delete_user(self, user_id: int) -> None:
        sql = "DELETE FROM \"User\" WHERE id = $1;"
        await self.execute(sql, user_id, execute=True)

    # Kanalni o'chirish
    async def delete_channel(self, channel_id: str) -> None:
        sql = "DELETE FROM \"Channel\" WHERE channel_id = $1;"
        await self.execute(sql, channel_id, execute=True)

    # Filmlarni o'chirish
    async def delete_movie(self, movie_id: int) -> None:
        sql = "DELETE FROM \"Movie\" WHERE id = $1;"
        await self.execute(sql, movie_id, execute=True)

    async def select_by_code_movie(self, code: str) -> Dict[str, Any]:
        sql = "SELECT * FROM \"Movie\" WHERE code = $1;"
        result = await self.execute(sql, code, fetch=True)
        # Return the first result or None if not found
        return result[0] if result else None

