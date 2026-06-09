from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# =====================================================================
# 1. Схема для користувача в сайдбарі (Sidebar)
# =====================================================================
class UserSidebarResponse(BaseModel):
    telegram_id: int
    username: Optional[str] = "Невідомий"
    current_theme: Optional[str] = "none" # Наш англійський дефолт: "tech_support", "billing_issue", "none"
    has_active_ticket: bool                # Щоб Vue знав, чи тикет зараз відкритий
    
    # --- НОВІ ПОЛЯ ДЛЯ ІНДИКАТОРІВ ---
    unread_count: int = 0                  # Кількість повідомлений з is_read=False
    last_message_text: Optional[str] = ""  # Текст останнього смс для прев'ю під нікнеймом
    last_message_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# =====================================================================
# 2. Схема для повідомлення у вікні чату (Chat History)
# =====================================================================
class MessageResponse(BaseModel):
    id: int
    user_id: int
    ticket_num: Optional[int] = None       # Номер тикета, до якого належить смс
    parent_id: Optional[int] = None        # ID оригіналу (для зв'язку пари оригінал/копія)
    
    # Може бути: "user", "bot", "our_admin_to_ext", "ext_admin", "our_admin_to_user"
    sender: str              
    text: Optional[str] = None             # Робимо Optional, бо повідомлення може бути чистим фото
    
    # --- НОВІ ПОЛЯ ДЛЯ МЕДІА ---
    file_id: Optional[str] = None
    file_type: str = "none"                # "photo", "document", "none"
    
    theme: Optional[str] = "none"
    msg_type: str = "text"                 # "ticket", "text"
    category: str = "none"                 # "tech", "billing"
    is_edited: bool = False
    is_read: bool = False                  # Щоб Vue підсвічував нечитані смс у самому чаті
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================================
# 3. НОВА СХЕМА: Для вхідних повідомлень від нашого адміна з Vue
# =====================================================================
# Вона знадобиться, коли адмін писатиме відповідь і тицятиме "Надіслати"
class AdminSendMessageRequest(BaseModel):
    text: str
    ticket_num: int
    parent_id: int                         # ID повідомлення, на яке ми відповідаємо/редагуємо