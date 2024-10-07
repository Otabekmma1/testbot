import logging
import aiohttp
from config import *
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from states import user_states
import asyncio

async def check_subscription(user_id):
    """Check if a user is subscribed to all required channels."""
    channels = await db.select_all_channels()  # Fetch channels from the database

    for channel in channels:
        chat_id = channel['channel_id']
        try:
            chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            if chat_member.status in ['left', 'kicked']:
                return False  # User is not subscribed
        except Exception as e:
            logging.error(f"Error checking subscription for channel {chat_id}: {e}")
            return False  # Assume not subscribed if an error occurs

    return True  # User is subscribed to all channels



async def ensure_subscription(message: Message):
    """Ensure the user is subscribed to the required channels."""
    user_id = message.from_user.id

    if not await check_subscription(user_id):
        await send_subscription_prompt(message)
        return False  # Indicate that the user is not subscribed
    return True  # User is subscribed

async def send_subscription_prompt(message: Message):
    """Send a subscription prompt to the user."""
    user_id = message.from_user.id

    # Remove old inline keyboard if exists
    if 'last_inline_message_id' in user_states.get(user_id, {}):
        await delete_previous_inline_message(message.chat.id, user_states[user_id]['last_inline_message_id'])

    inline_keyboard = await get_inline_keyboard_for_channels(user_id)
    sent_message = await message.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:", reply_markup=inline_keyboard)

    # Store the message ID for future reference
    user_states[user_id] = user_states.get(user_id, {})
    user_states[user_id]['last_inline_message_id'] = sent_message.message_id

async def delete_previous_inline_message(chat_id, message_id):
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception as e:
        logging.error(f"Failed to delete previous inline message: {e}")

async def get_inline_keyboard_for_channels(user_id):
    channels = await db.select_all_channels()  # Fetch channels from the database
    user_subscribed_channels = await check_subscription(user_id)  # Get user's subscribed channels

    inline_keyboard = []
    for channel in channels:
        channel_name = channel['name']
        channel_url = channel['url']
        inline_keyboard.append([InlineKeyboardButton(text=f"{channel_name}", url=channel_url)])

    # "A'zo bo'ldim" button
    inline_keyboard.append([InlineKeyboardButton(text="✅A'zo bo'ldim", callback_data='azo')])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
