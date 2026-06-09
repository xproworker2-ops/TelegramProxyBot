import os
import aiohttp
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from sqlalchemy import select, desc

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
async def save_to_db(
    user_id: int, 
    username: str, 
    text: str | None, 
    sender: str = "user", 
    theme: str = "none",
    msg_type: str = "text",
    category: str = "none",
    ticket_num: int | None = None,
    file_id: str | None = None,
    file_type: str = "none",
    parent_id: int | None = None
):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                user = User(telegram_id=user_id, username=username, current_theme=theme)
                session.add(user)
                await session.flush()
            else:
                if theme != "none":
                    user.current_theme = theme

            if theme == "none" and user:
                theme = user.current_theme

            # ВСЕ ПРОСТО: Нове повідомлення в базі = воно ще не прочитане адміном!
            message_record = Message(
                user_id=user_id,
                sender=sender,
                text=text,
                theme=theme,
                msg_type=msg_type,
                category=category,
                ticket_num=ticket_num,
                file_id=file_id,
                file_type=file_type,
                parent_id=parent_id,
                is_read=False  # Завжди за замовчуванням False
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

    # Мітимо як команду
    await save_to_db(user_id, username, message.text, sender="user", msg_type="command")

    reply_text = "Привіт! Я твій бот-проксі. Оберіть тему для обговорення, натиснувши на одну з кнопок нижче:"
    await message.answer(reply_text, reply_markup=get_themes_reply_keyboard())

    # Відповідь бота мітимо як звичайний текст
    await save_to_db(user_id, username, reply_text, sender="bot", msg_type="text")


# ОБРОБНИК НАТИСКАННЯ НА КНОПКИ З ТЕМАМИ
@router.message(F.text.in_({"🛠️ Технічна підтримка", "💳 Питання оплати"}))
async def handle_theme_click(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "без_юзернейму"
    ticket_id = message.message_id
    
    # Конвертуємо красивий текст кнопки в чистий системний id
    system_theme = "tech_support" if "Технічна" in message.text else "billing_issue"
    
    await save_to_db(
        user_id=user_id,
        username=username,
        text=f"Зміна теми на: {system_theme}",
        sender="user",
        theme=system_theme,
        msg_type="theme_change"
    )
    
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

    # 1. Визначаємо, чи прийшов файл, і дістаємо його file_id та текст (підпис)
    extracted_text = message.text or message.caption or "" # Беремо текст або підпис під фото
    extracted_file_id = None
    extracted_file_type = "none"

    if message.photo:
        # Telegram надсилає масив прев'юшок різних розмірів, беремо останню (найбільшу якість)
        extracted_file_id = message.photo[-1].file_id
        extracted_file_type = "photo"
    elif message.document:
        extracted_file_id = message.document.file_id
        extracted_file_type = "document"

    # 2. Читаємо стан юзера з бази
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()
            current_theme = user.current_theme if user else "none"
            has_active = user.has_active_ticket if user else False

    # СЦЕНАРІЙ А: У юзера ВЖЕ Є активний тикет і він дописує текст або надсилає ФАЙЛ (Бот мовчить)
    if has_active:
        async with async_session() as session:
            async with session.begin():
                ticket_query = await session.execute(
                    select(Message)
                    .where(Message.user_id == user_id, Message.msg_type == "ticket")
                    .order_by(Message.id.asc())
                )
                first_ticket = ticket_query.scalars().first()
                orig_ticket_num = first_ticket.ticket_num if first_ticket else message.message_id
                orig_theme = first_ticket.theme if first_ticket else "tech_support"
        
        category = "tech" if "tech" in orig_theme else "billing"
        
        # Мовчки зберігаємо доповнення (це може бути чисте фото/документ без тексту!)
        await save_to_db(
            user_id=user_id,
            username=username,
            text=extracted_text, 
            sender="user",
            theme=orig_theme,
            msg_type="ticket",
            category=category,
            ticket_num=orig_ticket_num,
            file_id=extracted_file_id,     # Передаємо файл
            file_type=extracted_file_type   # Передаємо тип файлу
        )
        
        # Для зовнішнього API формуємо інфо-рядок
        api_log = f"[Доповнення №{orig_ticket_num} (Файл: {extracted_file_type})]: {extracted_text}"
        await send_to_external_api(user_id, username, api_log)
        return

    # СЦЕНАРІЙ Б: Юзер флудить/шле файли без обраної теми
    if current_theme == "none":
        await message.answer(
            "Будь ласка, спочатку оберіть тему за допомогою кнопок, а потім надсилайте опис чи файли:",
            reply_markup=get_themes_reply_keyboard(),
        )
        return

    # СЦЕНАРІЙ В: Створення НОВОГО першого тикета (який теж може містити фото з описом)
    try:
        await message.delete()
    except Exception as e:
        print(f"[ПОМИЛКА ВИДАЛЕННЯ]: {e}")

    new_ticket_num = message.message_id - 2
    category = "tech" if "tech" in current_theme else "billing"
    display_theme_name = "🛠️ Технічна підтримка" if category == "tech" else "💳 Питання оплати"
    
    # Гарний опис для зворотного зв'язку
    media_label = "📎 (Прикріплено файл) " if extracted_file_type != "none" else ""
    formatted_text = f"Звернення №{new_ticket_num}\nТема: {display_theme_name}\n\n{media_label}{extracted_text}"

    # Зберігаємо перший головний меседж тикета
    await save_to_db(
        user_id=user_id,
        username=username,
        text=extracted_text,
        sender="user",
        theme=current_theme,
        msg_type="ticket",
        category=category,
        ticket_num=new_ticket_num,
        file_id=extracted_file_id,
        file_type=extracted_file_type
    )

    # Виводимо підтвердження в чат. Якщо це було фото, бот може продублювати його юзеру, 
    # але простіше надіслати текстову картку-підтвердження
    await message.answer(formatted_text)

    # Вмикаємо режим активного тикета
    async with async_session() as session:
        async with session.begin():
            res = await session.execute(select(User).where(User.telegram_id == user_id))
            db_user = res.scalar_one_or_none()
            if db_user:
                db_user.current_theme = "none"
                db_user.has_active_ticket = True

    reply_text = "Дякуємо! Ваш запит з медіа-файлом прийнято. Очікуйте на відповідь оператора."
    await message.answer(reply_text)
    
    await save_to_db(user_id, username, reply_text, sender="bot", msg_type="text", theme=current_theme)
    await send_to_external_api(user_id, username, f"Створено тикет №{new_ticket_num} з файлом ({extracted_file_type})")