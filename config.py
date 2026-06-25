import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '8900158435:AAHr45o_9BB0HQ4v16fQjgfzBFX5MM0C7PI')
DB_PATH = 'music_bot.db'