from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *
from typing import List, Dict, Any


def start_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍Kino kodlarini qidirish", url="https://t.me/codermovie")],
        [InlineKeyboardButton(text="🤖 Telegram bot yasatish", url="https://t.me/otabek_mma1")]
    ])
def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔈 Kanal", callback_data='manage_channel'),
        InlineKeyboardButton(text="🎥 Kino", callback_data='manage_movie')],
        # [InlineKeyboardButton(text="➕ Kino qo'shish", callback_data='add_movie')],
        [InlineKeyboardButton(text="📣 Xabar yuborish", callback_data='send_message'),
         InlineKeyboardButton(text="📊 Statistika", callback_data='stats')],
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='index')]
    ])

def movie_manage_keyboards():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kino qo'shish", callback_data='add_movie'),
         InlineKeyboardButton(text="❌ Kino o'chirish", callback_data='delete_movie')],
        [InlineKeyboardButton(text="👁 Mavjud kinolar", callback_data="show_movies")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data='back'),
         InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='index')],
    ])
def channel_manage_keyboards():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data='add_channel'),
         InlineKeyboardButton(text="❌ Kanal o'chirish", callback_data='delete_channel')],
        [InlineKeyboardButton(text="👁 Mavjud kanallar", callback_data="show_channels")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data='back'),
         InlineKeyboardButton(text="🏠 Bosh menyu", callback_data='index')]
    ])




async def show_channels(callback_query: CallbackQuery):
    channels = await db.select_all_channels()  # Fetch all channels from the database
    inline_buttons = []

    for channel in channels:
        channel_id = channel['channel_id']  # Assuming your channel data has a 'channel_id'
        channel_name = channel['name']
        channel_url = channel['url']# Assuming your channel data has a 'name'

        # Create a button for each channel with deletion callback
        button = InlineKeyboardButton(
            text=channel_name,
            url=channel_url  # Unique callback data for deletion
        )
        inline_buttons.append(button)

    # Create a back button
    back_button = InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_channel")

    # Add back button to the keyboard
    inline_buttons.append(back_button)  # Append back button to the inline_buttons list

    # Create the InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])  # Set the inline_keyboard property


    await callback_query.message.edit_text("Mavjud kanallar:", reply_markup=keyboard)




async def channel_keyboard():
    channels = await db.select_all_channels()  # Fetch all channels from the database

    inline_buttons = []

    for channel in channels:
        channel_id = channel['channel_id']  # Assuming your channel data has a 'channel_id'
        channel_name = channel['name']  # Assuming your channel data has a 'name'

        # Create a button for each channel with deletion callback
        button = InlineKeyboardButton(
            text=channel_name,
            callback_data=f"delete_channel_{channel_id}"  # Unique callback data for deletion
        )
        inline_buttons.append(button)

    # Create a back button
    back_button = InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_channel")

    # Add back button to the keyboard
    inline_buttons.append(back_button)  # Append back button to the inline_buttons list

    keyboard = InlineKeyboardMarkup(inline_keyboard=[inline_buttons])  # Set the inline_keyboard property

    return keyboard




# Function to = an inline keyboard for movies with pagination
async def generate_movies_keyboard(movies: List[Dict[str, Any]], page: int = 1) -> InlineKeyboardMarkup:
    MOVIES_PER_PAGE = 10
    total_movies = len(movies)
    total_pages = (total_movies + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE  # Calculate total pages

    # Determine the range of movies for the current page
    start_idx = (page - 1) * MOVIES_PER_PAGE
    end_idx = start_idx + MOVIES_PER_PAGE
    current_movies = movies[start_idx:end_idx]

    # Create a list to store rows of inline buttons
    keyboard_buttons = []
    count = start_idx  # Initialize count based on the current page
    for movie in current_movies:
        count += 1
        title = movie['title']
        code = movie['code']
        keyboard_buttons.append([InlineKeyboardButton(text=f"{count}. {title} - {code}", callback_data=f"movie:{code}")])

    # Pagination logic
    pagination_buttons = []

    # Display page numbers with "..." if necessary
    if total_pages > 1:
        if page > 1:
            pagination_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"movies_page:{page - 1}"))

        # Display the first two pages
        if page > 3:
            pagination_buttons.append(InlineKeyboardButton(text="1", callback_data="movies_page:1"))
            pagination_buttons.append(InlineKeyboardButton(text="2", callback_data="movies_page:2"))
            if page > 4:
                pagination_buttons.append(InlineKeyboardButton(text="...", callback_data="noop"))

        # Display current, previous, and next page numbers
        page_range = range(max(1, page - 1), min(total_pages, page + 2) + 1)
        for p in page_range:
            if p == page:
                pagination_buttons.append(InlineKeyboardButton(text=f"• {p} •", callback_data="noop"))
            else:
                pagination_buttons.append(InlineKeyboardButton(text=str(p), callback_data=f"movies_page:{p}"))

        # Display the last two pages if not already in the range
        if page < total_pages - 2:
            if page < total_pages - 3:
                pagination_buttons.append(InlineKeyboardButton(text="...", callback_data="noop"))
            pagination_buttons.append(InlineKeyboardButton(text=str(total_pages - 1), callback_data=f"movies_page:{total_pages - 1}"))
            pagination_buttons.append(InlineKeyboardButton(text=str(total_pages), callback_data=f"movies_page:{total_pages}"))

        # Add the "Next" button if there are more pages
        if page < total_pages:
            pagination_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"movies_page:{page + 1}"))

    # Add pagination buttons to the keyboard
    if pagination_buttons:
        keyboard_buttons.append(pagination_buttons)
    keyboard_buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="manage_movie")])

    # Create and return the inline keyboard markup
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

