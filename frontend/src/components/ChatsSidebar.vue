<template>
  <aside class="tg-chats-sidebar">
    <div class="tg-tabs">
      <button 
        v-for="tab in ['tech', 'billing', 'archive']" 
        :key="tab"
        :class="['tg-tab-btn', { active: store.currentTab === tab }]"
        @click="changeTab(tab)"
      >
        {{ tab === 'tech' ? 'Технічна' : tab === 'billing' ? 'Оплата' : 'Finera' }}
        <span class="tab-badge" v-if="getTabCount(tab) > 0">
          {{ getTabCount(tab) }}
        </span>
      </button>
    </div>

    <div class="tg-chats-list">
      <div 
        v-for="ticket in store.filteredTickets" 
        :key="ticket.id"
        :class="['tg-chat-item', { active: store.selectedTicket?.id === ticket.id }]"
        @click="store.selectTicket(ticket)"
      >
        <div class="chat-avatar">
          {{ ticket.username ? ticket.username[0].toUpperCase() : '?' }}
        </div>
        <div class="chat-info">
          <div class="chat-header">
            <span class="chat-name">@{{ ticket.username }}</span>
            <span class="chat-time">{{ ticket.time }}</span>
          </div>
          <p class="chat-last-msg">{{ ticket.message }}</p>
        </div>
      </div>
      <div v-if="store.filteredTickets.length === 0" class="tg-empty-txt">
        Нічого не знайдено
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useTicketStore } from '../stores/tickets'
const store = useTicketStore()

const changeTab = (tab) => {
  store.currentTab = tab
  if (typeof store.fetchTickets === 'function') store.fetchTickets()
}

const getTabCount = (tab) => {
  if (!store.tickets) return 0
  return store.tickets.filter(t => t.category === tab).length
}
</script>

<style scoped>
.tg-chats-sidebar {
  width: 320px;
  background-color: white;
  border-right: 1px solid #dfe1e5;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.tg-tabs {
  display: flex;
  background-color: white;
  border-bottom: 1px solid #dfe1e5;
  padding: 5px;
  gap: 4px;
}
.tg-tab-btn {
  flex: 1;
  background: none;
  border: none;
  color: #707579;
  padding: 8px 0;
  font-size: 0.85rem;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 500;
  position: relative;
}
.tg-tab-btn.active {
  color: #3390ec;
  background-color: #f4f9fe;
}
.tg-tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 20%;
  width: 60%;
  height: 3px;
  background-color: #3390ec;
  border-radius: 3px;
}
.tab-badge {
  background-color: #8db5dd;
  color: white;
  font-size: 0.75rem;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 3px;
}
.tg-chats-list {
  flex-grow: 1;
  overflow-y: auto;
}
.tg-chat-item {
  display: flex;
  padding: 10px 12px;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.15s;
  border-bottom: 1px solid #f4f4f5;
}
.tg-chat-item:hover { background-color: #f4f4f5; }
.tg-chat-item.active { background-color: #3390ec; color: white; border-bottom-color: #3390ec; }
.chat-avatar {
  width: 48px;
  height: 48px;
  background-color: #72b1e8;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: bold;
  font-size: 1.2rem;
  color: white;
  flex-shrink: 0;
}
.chat-info {
  flex-grow: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3px;
}
.chat-name { font-weight: 600; font-size: 0.95rem; color: #1a1a1a; }
.tg-chat-item.active .chat-name { color: white; }
.chat-time { font-size: 0.8rem; color: #a1aab3; }
.tg-chat-item.active .chat-time { color: #c0dcf7; }
.chat-last-msg {
  font-size: 0.85rem;
  color: #707579;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tg-chat-item.active .chat-last-msg { color: #f0f7ff; }
.tg-empty-txt { text-align: center; color: #a1aab3; font-size: 0.9rem; margin-top: 20px; font-style: italic; }
</style>