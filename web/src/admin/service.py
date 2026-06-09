from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from database.models import User, Message  # Твої моделі
from aiogram import Bot
import os

# Ініціалізуємо бота для надсилання сповіщень (наприклад, при закритті тикета)
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

class AdminService:
    
    # 1. Запит для сайдбару: дістаємо всіх унікальних юзерів та рахуємо індикатори
    @classmethod
    async def get_all_users(cls, session: AsyncSession):
        # Дістаємо всіх користувачів
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        sidebar_data = []
        
        for user in users:
            # Рахуємо, скільки у цього юзера непрочитаних повідомлень від нього самого або стороннього адміна
            # (нечитані повідомлення від нашого адміна чи бота рахувати не треба)
            unread_res = await session.execute(
                select(func.count(Message.id))
                .where(
                    Message.user_id == user.telegram_id,
                    Message.is_read == False,
                    Message.sender.in_(["user", "ext_admin"])
                )
            )
            unread_count = unread_res.scalar_one() or 0
            
            # Дістаємо останнє повідомлення для прев'ю під нікнеймом
            last_msg_res = await session.execute(
                select(Message)
                .where(Message.user_id == user.telegram_id)
                .order_by(Message.id.desc())
                .limit(1)
            )
            last_msg = last_msg_res.scalar_one_or_none()
            
            # Формуємо дані чітко під нашу Pydantic-схему UserSidebarResponse
            sidebar_data.append({
                "telegram_id": user.telegram_id,
                "username": user.username or "Невідомий",
                "current_theme": user.current_theme,
                "has_active_ticket": user.has_active_ticket,
                "unread_count": unread_count,
                "last_message_text": last_msg.text if last_msg else "",
                "last_message_time": last_msg.created_at if last_msg else None
            })
            
        return sidebar_data

    # 2. Запит для чату: дістаємо історію повідомлень та ОДРАЗУ робимо їх прочитаними
    @classmethod
    async def get_user_messages(cls, session: AsyncSession, telegram_id: int):
        # Спочатку дістаємо всі повідомлення для Vue
        result = await session.execute(
            select(Message)
            .where(Message.user_id == telegram_id)
            .order_by(Message.id.asc())
        )
        messages = result.scalars().all()
        
        if messages:
            # Коли адмін відкрив цей чат, логічно, що він ЗАРАЗ бачить усі ці повідомлення.
            # Тому ми автоматично оновлюємо статус усіх нечитаних повідомлень цього юзера на True (прочитано)!
            await session.execute(
                update(Message)
                .where(
                    Message.user_id == telegram_id,
                    Message.is_read == False
                )
                .values(is_read=True)
            )
            await session.commit()
            
        return messages

    # 3. Метод для закриття тикета (який ми викликаємо з роутера close_ticket)
    @classmethod
    async def close_user_ticket(cls, session: AsyncSession, user_id: int) -> bool:
        result = await session.execute(select(User).where(User.telegram_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.has_active_ticket:
            return False
            
        # Скидаємо прапорці активного тикета
        user.has_active_ticket = False
        user.current_theme = "none"
        
        await session.commit()
        
        # Надсилаємо клієнту в Телеграм сповіщення через бота
        try:
            await bot.send_message(
                chat_id=user_id, 
                text="🔒 **Ваше звернення було успішно вирішено та закрито оператором.**\nДякуємо, що звернулися!"
            )
        except Exception as e:
            print(f"[ТГ Помилка закриття]: {e}")
            
        return True