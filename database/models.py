from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, func, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Зберігаємо системну тему: "tech_support", "billing_issue", "none"
    current_theme: Mapped[str] = mapped_column(String(50), default="none")
    has_active_ticket: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    messages: Mapped[list["Message"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.telegram_id"), nullable=False)
    ticket_num: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("messages.id"), nullable=True)
    
    # Хто відправив повідомлення
    sender: Mapped[str] = mapped_column(String(30), nullable=False)  
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Поля для роботи з медіа-файлами
    file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    
    theme: Mapped[str] = mapped_column(String(50), default="none")
    msg_type: Mapped[str] = mapped_column(String(30), default="text", nullable=False)
    category: Mapped[str] = mapped_column(String(20), default="none", nullable=False)
    is_edited: Mapped[bool] = mapped_column(default=False, nullable=False)
    

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="messages")