import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useTicketStore = defineStore('tickets', () => {
  const currentTab = ref('tech')
  const selectedTicket = ref(null)

  // Глобальний стан фільтрів
  const filters = ref({
    id: '',
    status: '',
    text: '',
    date: '',
    userClass: ''
  })

  const tickets = ref([
    { id: 101, username: 'ivan_dev', message: 'Не працює проксі на другому сервері, помилка тайм-ауту.', time: '14:05', category: 'tech', status: 'new', userClass: 'VIP', date: '2026-06-09', replies: [] },
    { id: 103, username: 'alex_k', message: 'Як оновити конфіг для тунелю через термінал на Ubuntu?', time: '14:20', category: 'tech', status: 'in_progress', userClass: 'Regular', date: '2026-06-09', replies: [] },
    { id: 102, username: 'mari_biz', message: 'Оплатила підписку на місяць, але баланс досі не оновився.', time: '14:12', category: 'billing', status: 'new', userClass: 'Premium', date: '2026-06-08', replies: [] },
    { id: 99, username: 'user32', message: 'Дякую, все запрацювало після рестарту.', time: '13:50', category: 'archive', status: 'closed', userClass: 'Regular', date: '2026-06-07', replies: [] }
  ])

  // Функція для скидання фільтрів
  const resetFilters = () => {
    filters.value = { id: '', status: '', text: '', date: '', userClass: '' }
  }

  // Майбутній метод для запитів до FastAPI бекенду
  const fetchTickets = async () => {
    console.log('Робимо запит до API з параметрами:', {
      category: currentTab.value,
      ...filters.value
    })
    // Тут потім буде: const res = await axios.get('/api/tickets', { params: ... })
  }

  // Розумний фільтр на фронтенді (працює вже зараз для тестів)
  const filteredTickets = computed(() => {
    return tickets.value.filter(ticket => {
      if (ticket.category !== currentTab.value) return false
      if (filters.value.id && !String(ticket.id).includes(filters.value.id)) return false
      if (filters.value.status && ticket.status !== filters.value.status) return false
      if (filters.value.userClass && ticket.userClass !== filters.value.userClass) return false
      if (filters.value.date && ticket.date !== filters.value.date) return false
      if (filters.value.text) {
        const search = filters.value.text.toLowerCase()
        return ticket.message.toLowerCase().includes(search) || ticket.username.toLowerCase().includes(search)
      }
      return true
    })
  })

  const selectTicket = (ticket) => {
    selectedTicket.value = ticket
  }

  const sendReply = (text) => {
    if (!selectedTicket.value || !text.trim()) return
    const now = new Date()
    selectedTicket.value.replies.push({
      text,
      time: `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    })
  }

  const archiveCurrentTicket = () => {
    if (!selectedTicket.value) return
    selectedTicket.value.category = 'archive'
    selectedTicket.value.status = 'closed'
    selectedTicket.value = null
  }

  return {
    currentTab,
    selectedTicket,
    filters,
    filteredTickets,
    resetFilters,
    fetchTickets,
    selectTicket,
    sendReply,
    archiveCurrentTicket
  }
})