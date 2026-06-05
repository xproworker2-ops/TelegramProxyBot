import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()


async def run_bot():
    from aiogram.types import BotCommand  # Імпортуємо клас для команд меню
    from bot import bot, dp
    from database.connection import init_db

    print("[БАЗА ДАНИХ] Перевірка готовності бази...")
    for attempt in range(1, 6):
        try:
            await init_db()
            print("[БАЗА ДАНИХ] Успішно підключено, таблиці готові!")
            break
        except Exception as e:
            print(f"[БАЗА ДАНИХ] Спроба {attempt}/5 невдала: {e}")
            await asyncio.sleep(2)
    else:
        print(
            "[КРИТИЧНА ПОМИЛКА] Не вдалося підключитися до бази даних після 5 спроб. Бот вимикається."
        )
        sys.exit(1)

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("[ПОМИЛКА] BOT_TOKEN не задано в .env")
        sys.exit(1)

    # --- НАЛАШТУВАННЯ КНОПКИ МЕНЮ ДЛЯ МОБІЛОК ---
    # Це додасть кнопку "Menu" ліворуч від поля введення на будь-якому смартфоні
    try:
        main_menu_commands = [
            BotCommand(
                command="/start", description="Виберіть тему вашого звернення"
            )
        ]
        await bot.set_my_commands(main_menu_commands)
        print("[БОТ] Кнопка меню команд успішно налаштована.")
    except Exception as e:
        print(f"[ПОМИЛКА НАЛАШТУВАННЯ МЕНЮ]: {e}")
    # ---------------------------------------------

    print("[БОТ] Бот успішно запустився і готовий до роботи...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def run_web():
    import uvicorn

    print("[ВЕБ] Веб-сервер запускається на порту 8000...")
    uvicorn.run("web.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        run_web()
    else:
        asyncio.run(run_bot())