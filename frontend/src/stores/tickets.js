import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api/v1/admin'
const WS_URL = 'ws://localhost:8000/api/v1/admin/ws'

export const useTicketStore = defineStore('tickets', () => {
  const currentTab = ref('tech') 
  const selectedTicket = ref(null)
  const tickets = ref([])
  const filters = ref({ id: '', status: '', text: '', date: '', userClass: '' })
  const socket = ref(null)

  // 🔍 РЕАКТИВНА ФІЛЬТРАЦІЯ
  const filteredTickets = computed(() => {
    if (!tickets.value || !Array.isArray(tickets.value)) return []
    
    return tickets.value.filter(ticket => {
      let ticketTab = 'archive'
      
      if (ticket.current_theme === 'tech_support' || ticket.category === 'tech') {
        ticketTab = 'tech'
      } else if (ticket.current_theme === 'billing_issue' || ticket.category === 'billing') {
        ticketTab = 'billing'
      } else if (ticket.has_active_ticket === false) {
        ticketTab = 'archive'
      }

      if (ticketTab !== currentTab.value) return false

      if (filters.value.text && ticket.username) {
        const search = filters.value.text.toLowerCase()
        if (!ticket.username.toLowerCase().includes(search)) return false
      }

      return true
    })
  })

  // 🔌 ЖИВИЙ ВЕБ-СОКЕТ
  const initWebSocket = () => {
      // 1. Перевірка стану перед створенням нового з'єднання
      if (socket.value && socket.value.readyState !== WebSocket.CLOSED) {
          return;
      }

      console.log("🔌 [WS START]: Підключаємося до:", WS_URL)
      socket.value = new WebSocket(WS_URL)

      socket.value.onopen = () => {
          console.log("✅ [WS SUCCESS]: З'єднання встановлено!")
      }

      socket.value.onmessage = (event) => {
          // ... (ваш код обробки повідомлень залишається без змін)
      }

      socket.value.onclose = (event) => {
          console.warn(`⚠️ [WS CLOSE]: Код: ${event.code}. Реконнект через 3 сек...`)
          socket.value = null // Обов'язково скидаємо посилання
          setTimeout(initWebSocket, 3000)
      }
  }

  const fetchTickets = async () => {
    try {
      const response = await axios.get(`${API_URL}/users`)
      tickets.value = response.data
    } catch (error) {
      console.error("Помилка fetchTickets:", error)
    }
  }

  const selectTicket = async (ticket) => {
    selectedTicket.value = ticket
    try {
      const response = await axios.get(`${API_URL}/users/${ticket.telegram_id}/messages`, {
        params: { _t: Date.now() }
      })
      selectedTicket.value.messages_history = response.data
      ticket.unread_count = 0
      tickets.value = [...tickets.value] 
    } catch (error) {
      console.error("Помилка завантаження повідомлень:", error)
    }
  }

  const sendReply = async (text) => {
    if (!selectedTicket.value) return
    try {
      const response = await axios.post(`${API_URL}/messages/send-to-user`, {
        text,
        user_id: selectedTicket.value.telegram_id
      })

      if (response.data?.status === "success" || response.status === 200) {
        if (!selectedTicket.value.messages_history) selectedTicket.value.messages_history = []
        
        selectedTicket.value.messages_history.push({
          id: Date.now(),
          user_id: selectedTicket.value.telegram_id,
          sender: 'our_admin_to_user',
          text: text,
          created_at: new Date().toISOString()
        })
        
        selectedTicket.value = { ...selectedTicket.value }
      }
    } catch (error) {
      console.error("Помилка відправки повідомлення користувачу:", error)
    }
  }

  const resetFilters = () => {
    filters.value = { id: '', status: '', text: '', date: '', userClass: '' }
  }

  return {
    currentTab, selectedTicket, tickets, filters, filteredTickets,
    initWebSocket, fetchTickets, selectTicket, sendReply, resetFilters
  }
})