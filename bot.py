import asyncio
import logging
import sys
from handlers.handlers import register_handlers
from config import *

logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler(sys.stdout),
    logging.FileHandler('bot.log')
])

async def on_startup():
    await db.create_table_users()  # Create users table if not exists
    await db.create_table_movies()  # Create movies table if not exists
    await db.create_table_channels()

async def main():
    await db.create()  # Establish database connection
    await on_startup()
    register_handlers(dp)

    # Start the bot
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
