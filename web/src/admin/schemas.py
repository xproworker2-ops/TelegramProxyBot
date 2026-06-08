from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 1. Схема для користувача в сайдбарі (Sidebar)
class UserSidebarResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = "Невідомий"
    current_theme: Optional[str] = "Не обрано"

    class Config:
        from_attributes = True  # Дозволяє Pydantic автоматично конвертувати об'єкти SQLAlchemy в JSON


# 2. Схема для повідомлення у вікні чату (Chat History)
class MessageResponse(BaseModel):
    id: int
    user_id: int
    sender: str              # "user" або "bot"
    text: str
    theme: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True