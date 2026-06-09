from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        # Зберігаємо список усіх активних сокет-з'єднань (наших 3-5 адмінів)
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Викликається, коли адмін відкриває Vue і підключається"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS]: Адмін підключився. Активних сесій: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Викликається, коли адмін закриває вкладку чи оновлює сторінку"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WS]: Адмін відключився. Активних сесій: {len(self.active_connections)}")

    async def broadcast_new_message(self, ticket_num: int, sender: str, text: str | None):
        """Надсилає сигнал про НОВЕ повідомлення ВСІМ адмінам одночасно"""
        payload = {
            "event": "new_message",
            "ticket_num": ticket_num,
            "sender": sender,
            "text": text[:50] if text else "Файл/Медіа" # шматочок тексту для прев'ю в пуші
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception as e:
                # Якщо сокет "відвалився", але ми ще не встигли його видалити
                print(f"[WS Помилка розсилки]: {e}")

# Створюємо ОДИН глобальний екземпляр менеджера для всього проекту
ws_manager = ConnectionManager()