from .admin_pan import *
from .admin_movie import *
from .admin_channel import *
from .user_handlers import *
from config import *


def register_handlers(dp: Dispatcher):
    dp.message.register(start, CommandStart())
    dp.callback_query.register(start_callback, lambda c: c.data == "index")
    dp.message.register(search_movie_by_code_handler,lambda m: user_states.get(m.from_user.id, {}).get('state') == 'searching_movie')
    dp.message.register(admin_panel, lambda message: message.text == "/panel")
    dp.callback_query.register(callback_handler, lambda c: c.data == 'azo')  # Statistics handler
    dp.callback_query.register(add_movie_start, lambda c: c.data == 'add_movie')  # Add movie start handler
    dp.callback_query.register(send_message_prompt, lambda c: c.data == 'send_message')  # Send message prompt handler
    dp.callback_query.register(stats, lambda c: c.data == 'stats')  # Statistics handler
    dp.callback_query.register(manage_channel, lambda c: c.data == 'manage_channel')
    dp.callback_query.register(manage_movie, lambda c: c.data == 'manage_movie')
    dp.callback_query.register(process_back, lambda c: c.data == 'back')
    dp.callback_query.register(add_channel_start, lambda c: c.data == 'add_channel')
    dp.callback_query.register(delete_channel_start, lambda c: c.data == 'delete_channel')
    dp.callback_query.register(delete_movie_start, lambda c: c.data == 'delete_movie')
    dp.callback_query.register(show_channel, lambda c: c.data == 'show_channels')
    dp.callback_query.register(show_movies_command, lambda c: c.data == 'show_movies')
    dp.callback_query.register(movies_page_callback, lambda c: c.data.startswith('movies_page:'))
    dp.callback_query.register(movie_details_handler, lambda c: c.data.startswith('movie:'))

    # Message Handlers
    dp.message.register(
        add_movie,lambda message: isinstance(user_states.get(message.from_user.id), dict) and user_states[message.from_user.id].get('state') == 'adding_movie')  # Adding movie state handler
    dp.message.register(handle_send_message, lambda m: user_states.get(m.from_user.id, {}).get(
        'state') == 'sending_message')
    dp.message.register(add_chanel, lambda m: user_states.get(m.from_user.id, {}).get(
        'state') == 'adding_channel')
    dp.message.register(delete_movie_by_code, lambda m: user_states.get(m.from_user.id, {}).get(
        'state') == 'deleting_movie')

    dp.callback_query.register(delete_channel, lambda c: c.data.startswith('delete_channel_'))



    # Adding channel handler

