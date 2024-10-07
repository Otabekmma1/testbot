from aiogram.types import CallbackQuery, Message
from config import *
from keyboards.inline import *
from keyboards.default import *
from states import *
from subscrition import *
from .admin_pan import *

async def command_start_handler(message: Message, first_name: str):
    user_id = message.from_user.id
    if await check_subscription(user_id):
        keyboard = start_inline()
        user_states[user_id] = {'state': 'searching_movie'}
        await message.answer(f"<b>👋Salom {first_name}</b>\n\n<i>Kino kodini kiriting...</i>", reply_markup=keyboard,
                             parse_mode='html')
    else:
        await send_subscription_prompt(message)
async def manage_channel(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        await callback_query.answer("Sizda kanalni boshqarish huquqi mavjud emas.")
        return

    keyboard = channel_manage_keyboards()

    user_states[user_id] = {'state': 'manage_channel'}

    await callback_query.message.edit_text("Kanalni boshqarish:", reply_markup=keyboard)


async def add_channel_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        await callback_query.message.answer("Sizda kino qo'shish huquqi mavjud emas.")
        return
    user_states[user_id] = {'state': 'adding_channel', 'step': 'channel_id'}
    await callback_query.message.answer("Kanal ID sini kiriting:")


async def add_chanel(message: Message):
    user_id = message.from_user.id

    state = user_states[user_id]['step']
    # Handle the "🔙 Orqaga" action to go back
    if message.text == "🔙 Orqaga":
        await command_start_handler(message, message.from_user.first_name)
        return

    # Manage states
    if state == 'channel_id':
        user_states[user_id]['channel_id'] = message.text
        user_states[user_id]['step'] = 'name'
        await message.answer("Kanalning nomini yuboring.")

    elif state == 'name':
        user_states[user_id]['name'] = message.text
        user_states[user_id]['step'] = 'url'
        await message.answer("Kanalning URL sini yuboring.")

    elif state == 'url':
        user_states[user_id]['url'] = message.text
        await message.answer("Kanal muvaffaqiyatli qo'shildi!")

        # Save the channel to your database
        channel_id = user_states[user_id]['channel_id']
        name = user_states[user_id]['name']
        url = user_states[user_id]['url']

        await db.add_channel(channel_id, name, url)  # Ensure this function exists

        # Clean up user state
        user_states.pop(user_id, None)
        await admin_panel(message)

async def delete_channel_start(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in ADMINS:
        await callback_query.message.answer("Sizda kanal ochirish huquqi mavjud emas.")
        return
    reply_markup = await channel_keyboard()
    user_states[user_id] = {'state': 'delete_', 'step': 'channel_id'}
    await callback_query.message.edit_text("O'chirish uchun kanalni tanlang",
                                           reply_markup=reply_markup)  # Ensure `channel_keyboard()` returns the correct inline keyboard


async def delete_channel(callback_query: CallbackQuery):
    # Extract the channel ID from the callback data
    channel_id = callback_query.data[len("delete_channel_"):].strip()  # Remove "delete_" prefix

    try:
        # Delete the channel from the database
        await db.delete_channel(channel_id)

        # Acknowledge the deletion to the user
        await callback_query.answer(f"Kanal o'chirildi: {channel_id}")

        await admin_panel(callback_query.message)  # Ensure this function is defined to refresh the channel list
    except Exception as e:
        await callback_query.answer(f"Xatolik yuz berdi: {e}")

    # Optionally, you can delete the callback message after processing
    try:
        await callback_query.message.delete()  # Remove the callback message after processing
    except Exception as e:
        print(f"Error deleting message: {e}")

async def show_channel(callback_query: CallbackQuery):
    await show_channels(callback_query)