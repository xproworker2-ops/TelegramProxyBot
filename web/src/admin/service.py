from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, Message  # Імпортуємо твої моделі з глобальної папки

class AdminService:
    
    # Запит для сайдбару: дістаємо всіх унікальних юзерів
    @staticmethod
    async def get_all_users(session: AsyncSession):
        result = await session.execute(select(User))
        return result.scalars().all()

    # Запит для чату: дістаємо історію повідомлень конкретного юзера від старих до нових
    @staticmethod
    async def get_user_messages(session: AsyncSession, telegram_id: int):
        result = await session.execute(
            select(Message)
            .where(Message.user_id == telegram_id)
            .order_by(Message.id.asc())  # Сортування за зростанням, щоб чат йшов правильно
        )
        return result.scalars().all()