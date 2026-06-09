import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Отримуємо токен з .env
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Створюємо об'єкт бота
# DefaultBotProperties дозволяє встановити налаштування за замовчуванням (наприклад, Markdown)
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)