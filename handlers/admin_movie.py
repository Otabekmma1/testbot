from aiogram.types import Message, CallbackQuery
from config import *
from states import *
from handlers.user_handlers import command_start_handler
from keyboards.default import *
from keyboards.inline import *
from .admin_pan import *

async def manage_movie(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    keyboard = movie_manage_keyboards()
    user_states[user_id] = {'state': 'manage_movie'}
    await callback_query.message.edit_text("Kinoni boshqarish:", reply_markup=keyboard)


async def add_movie_start(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await message.answer("Sizda kino qo'shish huquqi mavjud emas.")
        return
    user_states[message.from_user.id] = {'state': 'adding_movie', 'step': 'title'}
    await message.answer("Kino nomini yuboring.")


async def add_movie(message: Message):
    user_id = message.from_user.id
    state = user_states[user_id]['step']

    if message.text == "🔙 Orqaga":
        await command_start_handler(message, message.from_user.first_name)
        return

    if state == 'title':
        user_states[user_id]['title'] = message.text
        user_states[user_id]['step'] = 'year'
        await message.answer("Kino yilini yuboring.")

    elif state == 'year':
        try:
            user_states[user_id]['year'] = int(message.text)
            user_states[user_id]['step'] = 'genre'
            await message.answer("Kino janrini yuboring.")
        except ValueError:
            await message.answer("Yil raqam bo'lishi kerak. Iltimos, qaytadan kiriting.")

    elif state == 'genre':
        user_states[user_id]['genre'] = message.text
        user_states[user_id]['step'] = 'language'
        await message.answer("Kino tilini yuboring.")

    elif state == 'language':
        user_states[user_id]['language'] = message.text
        user_states[user_id]['step'] = 'code'
        await message.answer("Kino kodini yuboring.")

    elif state == 'code':
        user_states[user_id]['code'] = message.text
        user_states[user_id]['step'] = 'video'
        await message.answer("Kino videosini yuklang (faqat MP4 format).")

    elif state == 'video':
        if message.video and message.video.mime_type == 'video/mp4':
            file_id = message.video.file_id

            title = user_states[user_id]['title']
            year = user_states[user_id]['year']
            genre = user_states[user_id]['genre']
            language = user_states[user_id]['language']
            code = user_states[user_id]['code']

            await db.add_movie(title, year, genre, language, code, file_id)

            await message.answer(f"Kino muvaffaqiyatli qo'shildi: {title}")

            user_states.pop(user_id, None)
            await admin_panel(message)
        else:
            await message.answer("Iltimos, MP4 formatidagi videoni yuboring.")


async def delete_movie_start(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Only allow admins to delete movies (if necessary)
    if user_id not in ADMINS:
        await callback.message.answer("Sizda kino o'chirish huquqi mavjud emas.")
        return

    user_states[user_id] = {'state': 'deleting_movie'}
    await callback.message.answer("Kino kodini kiriting:")


async def delete_movie_by_code(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id, {}).get('state')

    # Check if the user is in the process of deleting a movie
    if state == 'deleting_movie':
        movie_code = message.text

        # Query the movie from the database by code
        movie = await db.select_by_code_movie(movie_code) # Ensure this function exists

        if movie:
            await db.delete_movie(movie['id'])  # Delete the movie by its ID
            await message.answer(f"Kino muvaffaqiyatli o'chirildi: {movie['title']}")
            await admin_panel(message)
        else:
            await message.answer("Kino topilmadi, qayta urinib ko'ring.")

        # Clear user state after operation
        user_states.pop(user_id, None)



async def show_movies_command(callback_query: CallbackQuery):
    # Fetch all movies from the database
    movies = await db.select_all_movies()

    # Generate the inline keyboard for the first page
    keyboard = await generate_movies_keyboard(movies, page=1)

    # Send the message with the movie inline keyboard
    await callback_query.message.edit_text("Mavjud kinolar:", reply_markup=keyboard)


async def movies_page_callback(callback_query: CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    user_id = callback_query.from_user.id

    # Fetch all movies from the database
    movies = await db.select_all_movies()

    # Generate the inline keyboard for the current page
    keyboard = await generate_movies_keyboard(movies, page=page)
    user_states[user_id] = {'state': 'pagination'}

    # Edit the current message to show the updated keyboard
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


async def movie_details_handler(callback_query: CallbackQuery):
    code = callback_query.data.split(":")[1]  # Extract movie code from callback data

    movie = await db.select_by_code_movie(code)  # Define this function to get the movie data

    if movie:
        # Create a message with the movie details
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
                chat_id=callback_query.message.chat.id,  # Get the chat ID from the callback message
                video=movie['video_file_id'],  # Video file ID
                caption=caption,
                parse_mode='HTML'  # Enable HTML parsing
            )
    else:
        await callback_query.answer(text="❌ Kino topilmadi.", show_alert=True)

