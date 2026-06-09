<template>
  <section class="tg-chat-window">
    <div class="tg-chat-header">
      <div v-if="store.selectedTicket" class="chat-header-user">
        <span class="chat-name">Чат з @{{ store.selectedTicket.username }}</span>
        <span class="chat-status">тикет #{{ store.selectedTicket.id }}</span>
      </div>
      <div v-else class="chat-header-user">
        <span class="chat-name">Фільтрація звернень</span>
      </div>

      <div class="tg-filters-inline">
        <input 
          type="text" 
          v-model="store.filters.text" 
          placeholder="Пошук тексту..." 
          @input="store.fetchTickets"
          class="filter-input search-input"
        />
        <input 
          type="number" 
          v-model="store.filters.id" 
          placeholder="ID" 
          @input="store.fetchTickets"
          class="filter-input id-input"
        />
        <CustomSelect 
          v-model="store.filters.status"
          :options="statusOptions"
          placeholder="Усі статуси"
          @update:modelValue="store.fetchTickets"
          style="width: 125px;"
        />
        <CustomSelect 
          v-model="store.filters.userClass"
          :options="userClassOptions"
          placeholder="Усі класи"
          @update:modelValue="store.fetchTickets"
          style="width: 115px;"
        />
        <input 
          type="date" 
          v-model="store.filters.date" 
          @change="store.fetchTickets"
          class="filter-date"
        />
        <button class="btn-reset" @click="handleReset" title="Скинути фільтри">❌</button>
      </div>
    </div>

    <template v-if="store.selectedTicket">
      <div class="tg-chat-messages">
        <div class="msg-row user-msg">
          <div class="msg-bubble">
            <p>{{ store.selectedTicket.message }}</p>
            <span class="msg-time">{{ store.selectedTicket.time }}</span>
          </div>
        </div>

        <template v-if="store.selectedTicket.replies && store.selectedTicket.replies.length > 0">
          <div v-for="(reply, idx) in store.selectedTicket.replies" :key="idx" class="msg-row operator-msg">
            <div class="msg-bubble" v-if="reply">
              <p>{{ reply.text }}</p>
              <span class="msg-time">{{ reply.time }}</span>
            </div>
          </div>
        </template>
      </div>

      <div class="tg-chat-input-zone">
        <textarea 
          v-model="replyText" 
          placeholder="Напишіть повідомлення..." 
          @keydown.enter.prevent="handleSend"
        ></textarea>
        <button class="tg-send-btn" @click="handleSend">➡️</button>
      </div>
    </template>
    
    <div v-else class="tg-no-chat-selected">
      <span class="tg-select-hint">Виберіть тикет зліва або налаштуйте фільтри для пошуку</span>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useTicketStore } from '../stores/tickets'
import CustomSelect from './CustomSelect.vue'

const store = useTicketStore()
const replyText = ref('')

const statusOptions = [
  { value: '', label: 'Усі статуси' },
  { value: 'new', label: 'Нові' },
  { value: 'in_progress', label: 'В роботі' },
  { value: 'closed', label: 'Закриті' }
]

const userClassOptions = [
  { value: '', label: 'Усі класи' },
  { value: 'Regular', label: 'Regular' },
  { value: 'Premium', label: 'Premium' },
  { value: 'VIP', label: 'VIP' }
]

const handleSend = () => {
  if (!replyText.value.trim()) return
  store.sendReply(replyText.value)
  replyText.value = ''
}

const handleReset = () => {
  store.resetFilters()
  store.fetchTickets()
}

watch(() => store.selectedTicket, () => { replyText.value = '' })
</script>

<style scoped>
.tg-chat-window {
  flex-grow: 1;
  background-color: #f4f4f5;
  display: flex;
  flex-direction: column;
}
.tg-chat-header {
  height: 56px;
  background-color: white;
  border-bottom: 1px solid #dfe1e5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 10;
  flex-shrink: 0;
}
.chat-header-user { display: flex; flex-direction: column; }
.chat-name { font-weight: 600; font-size: 0.95rem; color: #1a1a1a; }
.chat-status { font-size: 0.8rem; color: #707579; }
.tg-filters-inline { display: flex; align-items: center; gap: 6px; }
.filter-input, .filter-date { background-color: #f4f4f5; border: 1px solid #dfe1e5; border-radius: 6px; padding: 6px 8px; font-size: 0.85rem; color: #1a1a1a; outline: none; }
.filter-input:focus, .filter-date:focus { border-color: #3390ec; background-color: white; }
.search-input { width: 130px; }
.id-input { width: 55px; text-align: center; }
.btn-reset { background: none; border: none; cursor: pointer; font-size: 0.85rem; padding: 4px; border-radius: 4px; }
.btn-reset:hover { background-color: #fee2e2; }
.tg-chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 20px 40px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg-row { display: flex; width: 100%; }
.user-msg { justify-content: flex-start; }
.operator-msg { justify-content: flex-end; }
.msg-bubble { max-width: 65%; padding: 8px 12px; border-radius: 12px; position: relative; box-shadow: 0 1px 1px rgba(0,0,0,0.1); }
.user-msg .msg-bubble { background-color: white; border-bottom-left-radius: 4px; color: #1a1a1a; }
.operator-msg .msg-bubble { background-color: #eeffde; border-bottom-right-radius: 4px; color: #1a1a1a; }
.msg-bubble p { font-size: 0.95rem; line-height: 1.4; word-break: break-word; margin-bottom: 4px; }
.msg-time { display: block; text-align: right; font-size: 0.75rem; color: #a1aab3; }
.tg-chat-input-zone { background-color: white; padding: 12px 25px; display: flex; gap: 15px; align-items: center; border-top: 1px solid #dfe1e5; }
.tg-chat-input-zone textarea { flex-grow: 1; background-color: #f4f4f5; border: 1px solid #dfe1e5; color: #1a1a1a; border-radius: 8px; padding: 10px 15px; resize: none; height: 42px; font-family: inherit; font-size: 0.95rem; }
.tg-chat-input-zone textarea:focus { outline: none; border-color: #3390ec; background-color: white; }
.tg-send-btn { background: none; border: none; font-size: 1.6rem; cursor: pointer; color: #3390ec; }
.tg-no-chat-selected { flex-grow: 1; display: flex; justify-content: center; align-items: center; background-color: #f4f4f5; }
.tg-select-hint { background-color: rgba(255, 255, 255, 0.9); padding: 8px 18px; border-radius: 15px; font-size: 0.9rem; color: #707579; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
</style>