import os
import aiohttp
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy import select

from database.connection import async_session
from database.models import User, Message

router = Router()
EXTERNAL_API_URL = "https://httpbin.org/post"


# 1. Функція для створення великих Reply-кнопок з темами (Тільки 2 теми)
def get_themes_reply_keyboard():
    builder = ReplyKeyboardBuilder() 
    builder.add(types.KeyboardButton(text="🛠️ Технічна підтримка"))
    builder.add(types.KeyboardButton(text="💳 Питання оплати"))
    builder.adjust(1)

    return builder.as_markup(
        resize_keyboard=True,
        persistent=True,
        input_field_placeholder="Оберіть тему для діалогу...",
    )


# 2. Функція для створення Inline-банера під текстом
def get_ticket_inline_banner(theme_name: str, ticket_id: int):
    short_theme = theme_name.split()[-1].capitalize()
    
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=f"📌 Тема: {short_theme} | 📂 Звернення №{ticket_id}",
                callback_data="info_banner_click"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Змінити тему / Скасувати",
                callback_data="cancel_ticket"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функція збереження історії в БД
async def save_to_db(user_id: int, username: str, text: str, sender: str = "user", theme: str | None = None):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.telegram_id == user_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    telegram_id=user_id,
                    username=username,
                    current_theme=theme or "Не обрано",
                )
                session.add(user)
                await session.flush()
            else:
                if theme:
                    user.current_theme = theme

            if theme is None:
                theme = user.current_theme

            message_record = Message(
                user_id=user_id,
                sender=sender,
                text=text,
                theme=theme,
            )
            session.add(message_record)


# Функція для відправки на стороннє API
async def send_to_external_api(user_id: int, username: str, text: str):
    payload = {
        "telegram_id": user_id,
        "username": username,
        "message_text": text,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                EXTERNAL_API_URL, json=payload, timeout=10
            ) as response:
                if response.status != 200:
                    print(f"[ПОМИЛКА API] Статус: {response.status}")
    except Exception as e:
        print(f"[ПОМИЛКА МЕРЕЖІ]: {e}")


# ОБРОБНИК КНОПКИ «СТАРТ»
@router.message(CommandStart())
async def command_start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_юзернейму"

    await save_to_db(user_id, username, message.text, sender="user")

    reply_text = "Привіт! Я твій бот-проксі. Оберіть тему для обговорення, натиснувши на одну з кнопок нижче:"
    await message.answer(reply_text, reply_markup=get_themes_reply_keyboard())

    await save_to_db(user_id, username, reply_text, sender="bot")


# ОБРОБНИК НАТИСКАННЯ НА КНОПКИ З ТЕМАМИ
@router.message(F.text.in_({"🛠️ Технічна підтримка", "💳 Питання оплати"}))
async def handle_theme_click(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_юзернейму"
    
    ticket_id = message.message_id
    
    await save_to_db(
        user_id,
        username,
        f"Зміна теми на: {message.text} (Тікет №{ticket_id})",
        sender="user",
        theme=message.text,
    )
    
    # Inline-банер з номером та кнопкою скасування ми кріпимо до повідомлення handles у handle_user_request
    # Але оскільки тут юзер має бачити банер, ми міняємо текст інструкції на сам банер.
    await message.answer(
        "Будь ласка, введіть ваше питання одним повідомленням:", 
        reply_markup=get_ticket_inline_banner(message.text, ticket_id)
    )


# ОБРОБНИКИ КЛІКІВ ПО INLINE-БАНЕРУ
@router.callback_query(F.data == "cancel_ticket")
async def process_cancel_ticket(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "без_юзернейму"
    
    await save_to_db(user_id, username, "Скасування теми користувачем", sender="user", theme="Не обрано")
    
    await callback_query.answer()
    await callback_query.message.delete()
    
    await callback_query.message.answer(
        "Звернення скасовано. Оберіть тему заново:",
        reply_markup=get_themes_reply_keyboard()
    )


@router.callback_query(F.data == "info_banner_click")
async def process_info_click(callback_query: types.CallbackQuery):
    await callback_query.answer()


# ОБРОБНИК УСІХ ІНШИХ ПОВІДОМЛЕНЬ (Введення самого питання з видаленням сирого тексту)
@router.message()
async def handle_user_request(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_юзернейму"

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()
            current_theme = user.current_theme if user else None

    if not current_theme or current_theme == "Не обрано":
        await message.answer(
            "Будь ласка, спочатку оберіть тему для діалогу. Натисніть одну з кнопок нижче:",
            reply_markup=get_themes_reply_keyboard(),
        )
        return

    # Номер тікета вираховується на основі message_id
    ticket_num = message.message_id - 2
    
    # 1. Видаляємо «сире» повідомлення юзера з чату, щоб не дублювати контент
    try:
        await message.delete()
    except Exception as e:
        print(f"[ПОМИЛКА ВИДАЛЕННЯ]: {e}")

    # Склеюємо номер, тему та текст
    formatted_text = f"Звернення №{ticket_num}\n{current_theme}\n\n{message.text}"

    # Записуємо фінальний склеєний рядок у БД
    await save_to_db(user_id, username, formatted_text, sender="user")

    # 2. Виводимо вже модифіковане повідомлення в чат
    await message.answer(formatted_text)

    # Дякуємо і повертаємо головне меню великих кнопок
    reply_text = "Дякуємо! Ваш запит прийнято в обробку. Будь ласка, зачекайте."
    await message.answer(reply_text, reply_markup=get_themes_reply_keyboard())

    await save_to_db(user_id, username, reply_text, sender="bot")
    await send_to_external_api(user_id, username, formatted_text)