import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/admin';
const WS_URL = 'ws://localhost:8000/api/v1/admin/ws';

export const useChatStore = defineStore('chat', {
  state: () => ({
    users: [],          // Список юзерів для сайдбару
    activeUserId: null, // ID поточного відкритого користувача
    messages: [],       // Історія чату поточного юзера
    socket: null,       // Наш вебсокет
  }),

  actions: {
    // 1. Завантажуємо юзерів для сайдбару при старті
    async fetchUsers() {
      try {
        const response = await axios.get(`${API_URL}/users`);
        this.users = response.data;
      } catch (error) {
        console.error("Помилка завантаження користувачів:", error);
      }
    },

    // 2. Відкриваємо чат з конкретним юзером
    async selectUser(userId) {
      this.activeUserId = userId;
      try {
        const response = await axios.get(`${API_URL}/users/${userId}/messages`);
        this.messages = response.data;
        
        // Як тільки відкрили чат — на фронтенді теж обнуляємо лічильник непрочитаних
        const user = this.users.find(u => u.telegram_id === userId);
        if (user) user.unread_count = 0;
      } catch (error) {
        console.error("Помилка завантаження чату:", error);
      }
    },

    // 3. Ініціалізація Вебсокета для реалтайм-індикаторів
    initWebSocket() {
      this.socket = new WebSocket(WS_URL);

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.event === "new_message") {
          // Шукаємо юзера в списку сайдбару
          const user = this.users.find(u => u.telegram_id === data.user_id);
          
          if (user) {
            user.last_message_text = data.text;
            user.last_message_time = new Date().toISOString();
            
            // Якщо цей чат зараз НЕ відкритий у адміна — збільшуємо лічильник
            if (this.activeUserId !== data.user_id) {
              user.unread_count++;
            }
          }

          // Якщо у адміна зараз відкритий саме ЦЕЙ чат — додаємо повідомлення в реалтаймі на екран
          if (this.activeUserId === data.user_id) {
            this.messages.push(data);
          }
        }
      };

      this.socket.onclose = () => {
        console.log("WS з'єднання закрилось. Перепідключаємось...");
        setTimeout(() => this.initWebSocket(), 3000); // авто-перепідключення
      };
    },

    // 4. Надіслати відповідь клієнту (our_admin_to_user)
    async sendResponseToUser(text, parentId, ticketNum) {
      try {
        // Шлемо POST запит на бек (ендпоінт, який ми розбирали раніше)
        const response = await axios.post(`${API_URL}/messages/send-to-user`, {
          text,
          parent_id: parentId,
          ticket_num: ticketNum,
          user_id: this.activeUserId
        });

        // Додаємо наше повідомлення в локальний чат, щоб адмін його одразу побачив
        if (response.data.status === "success") {
          this.messages.push({
            id: Date.now(), // тимчасовий ID
            user_id: this.activeUserId,
            sender: 'our_admin_to_user',
            text: text,
            parent_id: parentId,
            created_at: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error("Помилка відправки:", error);
      }
    },

    // 5. 🤖 МОКОВА ФУНКЦІЯ: Симуляція відповіді від стороннього адміна (ext_admin)
    triggerMockExternalAdminReply(text, parentId, ticketNum) {
      console.log("[MOCK]: Симулюємо відповідь від стороннього адміна...");
      
      // Імітуємо затримку в 2 секунди, ніби сторонній адмін подумав і відповів через API
      setTimeout(() => {
        const mockReply = {
          event: "new_message",
          id: Date.now(),
          user_id: this.activeUserId,
          ticket_num: ticketNum,
          parent_id: parentId,
          sender: "ext_admin", // <--- Важливо! Статус стороннього адміна
          text: `[Мок-Відповідь]: ${text}`,
          is_read: false,
          created_at: new Date().toISOString()
        };

        // Закидаємо в наш WebSocket-обробник, ніби воно прилетіло з сервера!
        this.socket.onmessage({ data: JSON.stringify(mockReply) });
      }, 2000);
    }
  }
});