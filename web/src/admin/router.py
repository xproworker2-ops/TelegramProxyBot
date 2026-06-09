from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Імпортуємо підключення до БД та менеджер сокетів
from database.connection import async_session 
from database.websocket_manager import ws_manager  # <-- ДОДАЛИ
from src.admin.schemas import UserSidebarResponse, MessageResponse
from src.admin.service import AdminService

router = APIRouter()

# Залежність (Dependency) для отримання сесії бази даних на кожен запит
async def get_db():
    async with async_session() as session:
        yield session

# --- 1. WEBSOCKET ЕНДПОІНТ ---
# Повний URL для Vue: ws://localhost:8000/api/v1/admin/ws
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Утримуємо з'єднання
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# --- 2. ЕНДПОІНТ ДЛЯ САЙДБАРУ (Повертає список юзерів) ---
@router.get("/users", response_model=List[UserSidebarResponse])
async def get_users_list(db: AsyncSession = Depends(get_db)):
    users = await AdminService.get_all_users(db)
    return users

# --- 3. ЕНДПОІНТ ДЛЯ ВІКНА ЧАТУ ---
@router.get("/users/{telegram_id}/messages", response_model=List[MessageResponse])
async def get_user_chat(telegram_id: int, db: AsyncSession = Depends(get_db)):
    messages = await AdminService.get_user_messages(db, telegram_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="Користувача або повідомлень не знайдено")
    return messages

# --- 4. ЕНДПОІНТ ДЛЯ ЗАКРИТТЯ ТИКЕТА ---
# Повний URL для Vue: POST /api/v1/admin/tickets/{user_id}/close
@router.post("/tickets/{user_id}/close")  # <-- Виправили на router і прибрали зайвий префікс
async def close_ticket(user_id: int, db: AsyncSession = Depends(get_db)):
    # Викликаємо логіку через сервіс, як і в інших ендпоінктах
    success = await AdminService.close_user_ticket(db, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Користувача не знайдено або тикет вже закритий")
        
    return {"status": "success", "message": "Ticket closed"}