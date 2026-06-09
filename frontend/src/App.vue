<template>
  <div class="tg-layout light-theme">
    <ChatsSidebar />

    <ChatWindow />

    <EditSidebar />
  </div>
</template>

<script setup>
import ChatsSidebar from './components/ChatsSidebar.vue'
import ChatWindow from './components/ChatWindow.vue'
import EditSidebar from './components/EditSidebar.vue'
</script>

<style>
.tg-layout.light-theme {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: white;
}
</style>