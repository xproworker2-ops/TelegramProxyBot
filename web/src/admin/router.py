from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# 1. Імпорти БД та налаштувань
from database.connection import async_session 
from database.models import User
from src.bot_instance import bot
from src.admin.ws_manager import ws_manager

# 2. Імпорти ваших сервісів та схем (ДОДАЙТЕ ЦЕ!)
from src.admin.schemas import UserSidebarResponse, MessageResponse
from src.admin.service import AdminService

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

# Ендпоінти
@router.get("/users", response_model=List[UserSidebarResponse])
async def get_users_list(db: AsyncSession = Depends(get_db)):
    return await AdminService.get_all_users(db)

@router.get("/users/{telegram_id}/messages", response_model=List[MessageResponse])
async def get_user_chat(telegram_id: int, db: AsyncSession = Depends(get_db)):
    messages = await AdminService.get_user_messages(db, telegram_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Повідомлень не знайдено")
    return messages

@router.post("/tickets/{user_id}/close")
async def close_ticket(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.telegram_id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        user.has_active_ticket = False
        user.current_theme = "Не обрано"
        await db.commit()
        await bot.send_message(
            chat_id=user_id, 
            text="🔒 Ваше звернення було успішно вирішено та закрито оператором."
        )
        return {"status": "success", "message": "Ticket closed"}
    raise HTTPException(status_code=404, detail="User not found")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)