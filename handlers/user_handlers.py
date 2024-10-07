from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from config import *
from subscrition import ensure_subscription, check_subscription, send_subscription_prompt
from states import user_states
import aiohttp
import logging
from aiogram.filters import CommandStart
from keyboards.inline import *
from keyboards.default import *

async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if not await ensure_subscription(message):
        return

    existing_users = await db.select_all_users()

    user_exists = any(user['telegram_id'] == user_id for user in existing_users)

    if user_exists:
        logging.info(f"User {username} already exists in the database.")
    else:
        logging.info(f"Adding new user {username} to the database.")
        await db.add_user(telegram_id=user_id, username=username)

        user_states[user_id] = {'state': 'searching_movie'}

    await command_start_handler(message, message.from_user.first_name)

async def start_callback(callback_query: CallbackQuery):
    first_name = callback_query.from_user.first_name
    user_id = callback_query.from_user.id

    keyboard = start_inline()
    user_states[user_id] = {'state': 'searching_movie'}
    await callback_query.message.edit_text(f"<b>👋Salom {first_name}</b>\n\n<i>Kino kodini kiriting...</i>", reply_markup=keyboard,
                         parse_mode='html')



async def command_start_handler(message: Message, first_name: str):
    user_id = message.from_user.id

    if await check_subscription(user_id):
        keyboard = start_inline()
        user_states[user_id] = {'state': 'searching_movie'}
        await message.answer(f"<b>👋Salom {first_name}</b>\n\n<i>Kino kodini kiriting...</i>", reply_markup=keyboard,
                             parse_mode='html')
    else:
        await send_subscription_prompt(message)


async def telegram_service_request(message: Message):
    user_id = message.from_user.id
    t = ("<b>🤖Telegram bot yaratish xizmati🤖</b>\n\n"
         "Admin: @otabek_mma1\n\n"
         "<i>Adminga bot nima haqida\n"
         "bot qanday vazifalarni bajarish kerak\n"
         "toliq malumot yozib qo'ying</i>\n\n"
         "Shunga qarab narxi kelishiladi")
    await message.answer(text=t, parse_mode='html')



async def search_movie_by_code(message: Message):
    user_id = message.from_user.id
    if not await ensure_subscription(message):
        return
    movie_code = message.text.strip()
    movie = await db.select_by_code_movie(movie_code)

    if movie:
        caption = (
            f"<b>🎬Nomi:</b> {movie['title']}\n"
            f"<b>📆Yili:</b> {movie['year']}\n"
            f"<b>🎞Janr:</b> {movie['genre']}\n"
            f"<b>🌍Tili:</b> {movie['language']}\n"
            f"<b>🗂Yuklash:</b> {movie['code']}\n\n"
            f"<b>🤖Bot:</b> @codermoviebot"
        )

        if movie['video_file_id']:
            await bot.send_video(
                chat_id=message.chat.id,
                video=movie['video_file_id'],
                caption=caption,
                parse_mode='HTML'
            )
        else:
            await message.answer("Kino videosi topilmadi.")
    else:
        await message.answer("Kino topilmadi")

    # Foydalanuvchidan yana kod kiritishini so'raymiz
    user_states[user_id] = {'state': 'searching_movie'}

# Holatni tekshiradigan handler
async def search_movie_by_code_handler(message: Message):
    await search_movie_by_code(message)
async def callback_handler(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    if await check_subscription(user_id):
        existing_users = await db.select_all_users()

        user_exists = any(user['telegram_id'] == user_id for user in existing_users)

        if user_exists:
            logging.info(f"User {username} already exists in the database.")
        else:
            logging.info(f"Adding new user {username} to the database.")
            await db.add_user(telegram_id=user_id, username=username)
            # Add new user to the user states
            user_states[user_id] = {'state': 'searching_movie'}

        # Call command_start_handler
        await command_start_handler(callback_query.message, callback_query.from_user.first_name)
    else:
        await send_subscription_prompt(callback_query.message)


