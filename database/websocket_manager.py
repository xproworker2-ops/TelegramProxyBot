# database/websocket_manager.py
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS]: Адмін підключився. Активних сесій: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS]: Адмін відключився. Активних сесій: {len(self.active_connections)}")

    # Універсальний метод, який викликає твій бот у handlers.py
    async def broadcast(self, data: dict):
        """Надсилає будь-який JSON-пайлоад усім активним адмінам"""
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"[WS Помилка розсилки]: {e}")

    # Залишаємо старий метод для зворотної сумісності, якщо він десь використовується
    async def broadcast_new_message(self, ticket_num: int, sender: str, text: str | None):
        payload = {
            "event": "new_message",
            "ticket_num": ticket_num,
            "sender": sender,
            "text": text[:50] if text else "Файл/Медіа"
        }
        await self.broadcast(payload)

ws_manager = ConnectionManager()