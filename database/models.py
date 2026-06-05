from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users" # Назва таблиці в базі даних
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    current_theme: Mapped[str] = mapped_column(String(100), default="Не обрано")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Зв'язок: один юзер може мати список багатьох повідомлень
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    sender: Mapped[str] = mapped_column(String(10)) # Хто написав: 'user' чи 'bot'
    text: Mapped[str] = mapped_column(Text)
    theme: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Зворотній зв'язок з таблицею користувача
    user: Mapped["User"] = relationship(back_populates="messages")