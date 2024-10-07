from aiogram.types import Message
from config import *
from states import user_states
from aiogram.types import CallbackQuery
from config import *
from keyboards.inline import *
from keyboards.default import *
import asyncio
from subscrition import *
from .admin_movie import *

async def process_back(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    state = user_states.get(user_id, {}).get('state')
    print(state)
    if state == 'manage_channel':
        keyboard = admin_keyboard()
        await callback_query.message.edit_text("Admin panel:", reply_markup=keyboard)
    elif state == 'adding_channel':
        keyboard = admin_keyboard()
        await callback_query.message.edit_text("Admin panel:", reply_markup=keyboard)
    elif state == 'delete_':
        keyboard = channel_manage_keyboards()
        await callback_query.message.edit_text("Kanalni boshqarish:", reply_markup=keyboard)
    elif state == 'adding_movie':
        keyboard = admin_keyboard()
        await callback_query.message.edit_text("Admin panel:", reply_markup=keyboard)
    elif state == 'manage_movie':
        keyboard = admin_keyboard()
        await callback_query.message.edit_text("Admin panel:", reply_markup=keyboard)
    elif state == 'deleting_movie':
        keyboard = admin_keyboard()
        await callback_query.message.edit_text("Admin panel:", reply_markup=keyboard)
    else:
        await callback_query.answer("Siz hozir orqaga qaytolmaysiz.")





async def admin_panel(message: Message):
    user_id = message.from_user.id
    if int(user_id) not in ADMINS:
        await message.answer("Sizda admin panelga kirish huquqi mavjud emas.")
        return

    keyboard = admin_keyboard()
    user_states[user_id] = {'state': 'admin_panel'}

    await message.answer("Admin panel:", reply_markup=keyboard)
async def send_message_prompt(callback_query: CallbackQuery):
    """Handler for the 'send_message' button - prompts admin to send a message."""
    await callback_query.message.answer("Xabar yuborish uchun xabar matnini yuboring (text, file, MP4, MP3).")
    user_states[callback_query.from_user.id] = {'state': 'sending_message'}


async def stats(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if not await ensure_subscription(callback_query.message):
        return

    total_users = len(await db.select_all_users())
    total_channels = len(await db.select_all_channels())
    total_movies = len(await db.select_all_movies())

    stats_message = (
        f"📊 Statistika:\n"
        f"• Kanallar: {total_channels}\n"
        f"• Filmlar: {total_movies}\n"
        f"• Foydalanuvchilar: {total_users}\n"
    )

    await callback_query.message.answer(stats_message)


async def handle_send_message(message: Message):
    """Admin xabar yuborayotganda har qanday kontentni qayta ishlash uchun handler."""
    user_id = message.from_user.id

    # Obunani tekshirish
    if not await ensure_subscription(message):
        return

    # Foydalanuvchilar ro'yxatini olish
    users = await db.select_all_users()  # Get users from the database

    sent_count = 0
    failed_count = 0

    # Xabarni barcha foydalanuvchilarga yuborish
    async def send_message_to_user(user_telegram_id):
        nonlocal sent_count, failed_count
        try:
            await bot.copy_message(user_telegram_id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent_count += 1
        except Exception as e:
            logging.error(f"Xabar yuborishda xatolik {user_telegram_id} ga: {e}")
            failed_count += 1

    # Barcha foydalanuvchilarga parallel yuborish uchun asyncio.gather'dan foydalanamiz
    tasks = [send_message_to_user(user['telegram_id']) for user in users]
    await asyncio.gather(*tasks)

    # Tasdiqlovchi xabarni admin foydalanuvchiga yuborish
    await message.answer(
        f"Xabar yuborildi:\n"
        f"✅ Muvaffaqiyatli: {sent_count} foydalanuvchi\n"
        f"❌ Xatoliklar: {failed_count} foydalanuvchi"
    )

    # Foydalanuvchi holatini qayta tiklash
    user_states[user_id] = {'state': 'searching_movie'}


