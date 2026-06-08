<template>
  <section class="tg-chat-window">
    <template v-if="store.selectedTicket">
      <div class="tg-chat-header">
        <div class="chat-header-user">
          <span class="chat-name">Чат з @{{ store.selectedTicket.username }}</span>
          <span class="chat-status">тикет #{{ store.selectedTicket.id }}</span>
        </div>
      </div>

      <div class="tg-chat-messages">
        <div class="msg-row user-msg">
          <div class="msg-bubble">
            <p>{{ store.selectedTicket.message }}</p>
            <span class="msg-time">{{ store.selectedTicket.time }}</span>
          </div>
        </div>

        <div v-for="(reply, idx) in store.selectedTicket.replies" :key="idx" class="msg-row operator-msg">
          <div class="msg-bubble">
            <p>{{ reply.text }}</p>
            <span class="msg-time">{{ reply.time }}</span>
          </div>
        </div>
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
      <span class="tg-select-hint">Виберіть тикет, щоб почати обробку</span>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useTicketStore } from '../stores/tickets'

const store = useTicketStore()
const replyText = ref('')

const handleSend = () => {
  if (!replyText.value.trim()) return
  store.sendReply(replyText.value)
  replyText.value = ''
}

// Очищуємо поле вводу, якщо оператор перемикає чат
watch(() => store.selectedTicket, () => {
  replyText.value = ''
})
</script>