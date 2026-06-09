<template>
  <div class="tg-layout light-theme">
    <ChatsSidebar />
    <ChatWindow />
    <EditSidebar />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useTicketStore } from './stores/tickets' // перевірь шлях до стори
import ChatsSidebar from './components/ChatsSidebar.vue'
import ChatWindow from './components/ChatWindow.vue'
import EditSidebar from './components/EditSidebar.vue'

const store = useTicketStore()

onMounted(() => {
  store.fetchTickets()     // Одразу вантажимо юзерів у сайдбар
  store.initWebSocket()    // Відкриваємо постійний живий канал зв'язку
})
</script>

<style>
.tg-layout.light-theme {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: white;
}
</style>