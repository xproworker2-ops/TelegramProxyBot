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

<style scoped>
.tg-edit-sidebar {
  width: 360px;
  background-color: white;
  border-left: 1px solid #dfe1e5;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.sidebar-block-title {
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  font-weight: 600;
  border-bottom: 1px solid #dfe1e5;
  color: #3390ec;
  flex-shrink: 0;
}
.edit-form {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.85rem; color: #707579; font-weight: 500; }
.form-group textarea {
  background-color: #f4f4f5;
  border: 1px solid #dfe1e5;
  color: #1a1a1a;
  padding: 10px;
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
}
.form-group textarea:focus { outline: none; border-color: #3390ec; background-color: white; }
.tg-btn {
  padding: 11px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s;
  font-size: 0.9rem;
}
.tg-btn-success { background-color: #3390ec; color: white; }
.tg-btn-success:hover { background-color: #2b7cc8; }
.tg-empty-txt { text-align: center; color: #a1aab3; font-size: 0.9rem; margin-top: 20px; font-style: italic; }
</style>