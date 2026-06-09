from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from database.models import User, Message  # Твої моделі
from src.bot_instance import bot

class AdminService:
    
    # 1. Запит для сайдбару: дістаємо всіх унікальних юзерів та рахуємо індикатори
    @classmethod
    async def get_all_users(cls, session: AsyncSession):
        result = await session.execute(select(User).order_by(User.created_at.desc()))
        users = result.scalars().all()
        
        sidebar_data = []
        
        for user in users:
            # ЗМІНЕНО: Рахуємо нечитані повідомлення ТІЛЬКИ якщо це реальний ticket або text від юзера
            unread_res = await session.execute(
                select(func.count(Message.id))
                .where(
                    Message.user_id == user.telegram_id,
                    Message.is_read == False,
                    Message.sender == 'user',
                    Message.msg_type.in_(['ticket', 'text']) # <-- Ігноруємо command та theme_change
                )
            )
            unread_count = unread_res.scalar_one() or 0
            
            # ЗМІНЕНО: Прев'ю останнього повідомлення — ігноруємо бота, беремо діалог
            last_msg_res = await session.execute(
                select(Message)
                .where(
                    Message.user_id == user.telegram_id,
                    Message.sender != 'bot',
                    Message.msg_type.in_(['ticket', 'text']) # <-- Тільки чиста суть діалогу
                )
                .order_by(Message.id.desc())
                .limit(1)
            )
            last_msg = last_msg_res.scalar_one_or_none()
            
            sidebar_data.append({
                "telegram_id": user.telegram_id,
                "username": user.username or "Невідомий",
                "current_theme": user.current_theme,
                "has_active_ticket": user.has_active_ticket,
                "unread_count": unread_count,
                "last_message_text": last_msg.text if last_msg else "Немає повідомлень",
                "last_message_time": last_msg.created_at if last_msg else None
            })
            
        return sidebar_data

    # 2. Запит для чату: дістаємо історію повідомлень та ОДРАЗУ робимо їх прочитаними
    @classmethod
    async def get_user_messages(cls, session: AsyncSession, telegram_id: int):
        # Вибираємо чисті повідомлення діалогу (юзер та відповіді адміна)
        result = await session.execute(
            select(Message)
            .where(
                Message.user_id == telegram_id,
                Message.sender != 'bot',
                Message.msg_type.in_(['ticket', 'text']) # <-- Фільтруємо за типом прямо в БД
            )
            .order_by(Message.id.asc())
        )
        messages = result.scalars().all()
        
        if messages:
            # Оновлюємо статус "прочитано" тільки для того, що реально показали адміну
            await session.execute(
                update(Message)
                .where(
                    Message.user_id == telegram_id,
                    Message.is_read == False,
                    Message.sender == 'user',
                    Message.msg_type.in_(['ticket', 'text'])
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
        if bot is not None:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text="🔒 **Ваше звернення було успішно вирішено та закрито оператором.**\nДякуємо, що звернулися!"
                )
            except Exception as e:
                print(f"[ТГ Помилка закриття]: {e}")
            
        return True