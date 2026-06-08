import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTicketStore = defineStore('tickets', () => {
  const currentTab = ref('tech')
  const selectedTicket = ref(null)

  const tickets = ref([
    { id: 101, username: 'ivan_dev', message: 'Не працює проксі на другому сервері, помилка тайм-ауту підключення.', time: '14:05', category: 'tech', internalNote: '', replies: [] },
    { id: 103, username: 'alex_k', message: 'Як оновити конфіг для тунелю через термінал на Ubuntu?', time: '14:20', category: 'tech', internalNote: 'Юзер новачок', replies: [] },
    { id: 102, username: 'mari_biz', message: 'Оплатила підписку на місяць, але баланс у боті досі не оновився.', time: '14:12', category: 'billing', internalNote: '', replies: [] },
    { id: 99, username: 'user32', message: 'Дякую, все запрацювало після рестарту.', time: '13:50', category: 'archive', internalNote: 'Успішно вирішено', replies: [{ text: 'Раді допомогти!', time: '13:52' }] }
  ])

  const getTicketsByTab = (tab) => {
    return tickets.value.filter(t => t.category === tab)
  }

  const selectTicket = (ticket) => {
    selectedTicket.value = ticket
  }

  const sendReply = (text) => {
    if (!selectedTicket.value || !text.trim()) return
    const now = new Date()
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
    
    selectedTicket.value.replies.push({
      text: text,
      time: timeStr
    })
  }

  const archiveCurrentTicket = () => {
    if (!selectedTicket.value) return
    selectedTicket.value.category = 'archive'
    selectedTicket.value = null
  }

  return {
    currentTab,
    selectedTicket,
    tickets,
    getTicketsByTab,
    selectTicket,
    sendReply,
    archiveCurrentTicket
  }
})