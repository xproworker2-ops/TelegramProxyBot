import os

import aiohttp
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не знайдено в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://httpbin.org/post")

async def send_to_external_api(user_id: int, username: str, text: str):
    payload = {
        "telegram_id": user_id,
        "username": username,
        "message_text": text,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(EXTERNAL_API_URL, json=payload, timeout=10) as response:
                if response.status == 200:
                    print(f"[УСПІХ] Дані від користувача {user_id} відправлено!")
                else:
                    print(f"[ПОМИЛКА API] Статус відповіді: {response.status}")
    except Exception as e:
        print(f"[ПОМИЛКА] Не вдалося зв'язатися з API: {e}")

from .handlers import router

dp.include_router(router)
