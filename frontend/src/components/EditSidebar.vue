<template>
  <aside class="tg-edit-sidebar">
    <div class="sidebar-block-title">Редагування тикета</div>
    
    <template v-if="store.selectedTicket">
      <div class="edit-form">
        <div class="form-group">
          <label>Текст запиту користувача:</label>
          <textarea v-model="store.selectedTicket.message" rows="6"></textarea>
        </div>

        <div class="form-group">
          <label>Внутрішня нотатка (не видно юзеру):</label>
          <textarea v-model="store.selectedTicket.internalNote" placeholder="Додати коментар для команди..."></textarea>
        </div>

        <div class="form-group actions-group">
          <button class="tg-btn tg-btn-success" @click="store.archiveCurrentTicket">
            📥 Закрити & Архівувати
          </button>
        </div>
      </div>
    </template>

    <div v-else class="tg-empty-txt" style="padding: 20px;">
      Виберіть тикет для редагування
    </div>
  </aside>
</template>

<script setup>
import { useTicketStore } from '../stores/tickets'
const store = useTicketStore()
</script>