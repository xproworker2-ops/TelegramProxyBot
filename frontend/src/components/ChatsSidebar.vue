<template>
  <aside class="tg-chats-sidebar">
    <div class="tg-tabs">
      <button 
        v-for="tab in ['tech', 'billing', 'archive']" 
        :key="tab"
        :class="['tg-tab-btn', { active: store.currentTab === tab }]"
        @click="store.currentTab = tab"
      >
        {{ tab === 'tech' ? 'Технічна' : tab === 'billing' ? 'Оплата' : 'Архів' }}
        <span class="tab-badge" v-if="store.getTicketsByTab(tab).length > 0">
          {{ store.getTicketsByTab(tab).length }}
        </span>
      </button>
    </div>

    <div class="tg-chats-list">
      <div 
        v-for="ticket in store.getTicketsByTab(store.currentTab)" 
        :key="ticket.id"
        :class="['tg-chat-item', { active: store.selectedTicket?.id === ticket.id }]"
        @click="store.selectTicket(ticket)"
      >
        <div class="chat-avatar">
          {{ ticket.username[0].toUpperCase() }}
        </div>
        <div class="chat-info">
          <div class="chat-header">
            <span class="chat-name">@{{ ticket.username }}</span>
            <span class="chat-time">{{ ticket.time }}</span>
          </div>
          <p class="chat-last-msg">{{ ticket.message }}</p>
        </div>
      </div>
      <div v-if="store.getTicketsByTab(store.currentTab).length === 0" class="tg-empty-txt">
        Нічого немає
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useTicketStore } from '../stores/tickets'
const store = useTicketStore()
</script>