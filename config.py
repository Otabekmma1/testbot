from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from db.postgresql import Database
import os
from dotenv import load_dotenv


load_dotenv()

TOKEN = '6565102114:AAHc6MfFofOoZXGDfHFvdmHmzr0i-0zsvj4'
ADMINS=[5541564692, 6565102114]

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db = Database()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
