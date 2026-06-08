from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_theme: Mapped[str] = mapped_column(String(100), default="Не обрано")
    
    # func.now() автоматично ставить CURRENT_TIMESTAMP на рівні MySQL
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Зв'язок: один юзер може мати список багатьох повідомлень
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    sender: Mapped[str] = mapped_column(String(10)) # 'user' чи 'bot'
    text: Mapped[str] = mapped_column(Text)          # Для великих текстів у MySQL
    theme: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Тут так само віддаємо генерацію часу на бік бази даних
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Зворотній зв'язок з таблицею користувача
    user: Mapped["User"] = relationship(back_populates="messages")