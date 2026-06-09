import os
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")

_PLACEHOLDER_TOKENS = {"", "your_telegram_bot_token_here"}

if BOT_TOKEN and BOT_TOKEN not in _PLACEHOLDER_TOKENS:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    )
else:
    bot = None
