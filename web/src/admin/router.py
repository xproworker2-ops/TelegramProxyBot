from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Імпортуємо підключення до БД з твоєї папки database
from database.connection import async_session 
from src.admin.schemas import UserSidebarResponse, MessageResponse
from src.admin.service import AdminService

router = APIRouter()

# Залежність (Dependency) для отримання сесії бази даних на кожен запит
async def get_db():
    async with async_session() as session:
        yield session

# 1. Ендпоінт для сайдбару (Повертає список юзерів)
@router.get("/users", response_model=List[UserSidebarResponse])
async def get_users_list(db: AsyncSession = Depends(get_db)):
    users = await AdminService.get_all_users(db)
    return users

# 2. Ендпоінт для вікна чату (Повертає історію повідомлень конкретного юзера)
@router.get("/users/{telegram_id}/messages", response_model=List[MessageResponse])
async def get_user_chat(telegram_id: int, db: AsyncSession = Depends(get_db)):
    messages = await AdminService.get_user_messages(db, telegram_id)
    if not messages and messages != []:
        raise HTTPException(status_code=404, detail="Користувача або повідомлень не знайдено")
    return messages