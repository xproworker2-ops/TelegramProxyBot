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
/* Скопіюй сюди ВЕСЬ блок <style> зі свого початкового варіанту світлої теми без змін */
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background-color: #f4f4f5;
  color: #1a1a1a;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  height: 100vh;
  overflow: hidden;
}
.tg-layout.light-theme { display: flex; height: 100vh; width: 100vw; background-color: white; }
.tg-chats-sidebar { width: 320px; background-color: white; border-right: 1px solid #dfe1e5; display: flex; flex-direction: column; }
.tg-tabs { display: flex; background-color: white; border-bottom: 1px solid #dfe1e5; padding: 5px; gap: 4px; }
.tg-tab-btn { flex: 1; background: none; border: none; color: #707579; padding: 8px 0; font-size: 0.85rem; cursor: pointer; border-radius: 6px; font-weight: 500; position: relative; }
.tg-tab-btn.active { color: #3390ec; background-color: #f4f9fe; }
.tg-tab-btn.active::after { content: ''; position: absolute; bottom: -6px; left: 20%; width: 60%; height: 3px; background-color: #3390ec; border-radius: 3px; }
.tab-badge { background-color: #8db5dd; color: white; font-size: 0.75rem; padding: 1px 6px; border-radius: 10px; margin-left: 3px; }
.tg-chats-list { flex-grow: 1; overflow-y: auto; }
.tg-chat-item { display: flex; padding: 10px 12px; gap: 12px; cursor: pointer; transition: background-color 0.15s; border-bottom: 1px solid #f4f4f5; }
.tg-chat-item:hover { background-color: #f4f4f5; }
.tg-chat-item.active { background-color: #3390ec; color: white; border-bottom-color: #3390ec; }
.chat-avatar { width: 48px; height: 48px; background-color: #72b1e8; border-radius: 50%; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 1.2rem; color: white; flex-shrink: 0; }
.chat-info { flex-grow: 1; overflow: hidden; display: flex; flex-direction: column; justify-content: center; }
.chat-header { display: flex; justify-content: space-between; margin-bottom: 3px; }
.chat-name { font-weight: 600; font-size: 0.95rem; color: #1a1a1a; }
.tg-chat-item.active .chat-name { color: white; }
.chat-time { font-size: 0.8rem; color: #a1aab3; }
.tg-chat-item.active .chat-time { color: #c0dcf7; }
.chat-last-msg { font-size: 0.85rem; color: #707579; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tg-chat-item.active .chat-last-msg { color: #f0f7ff; }
.tg-chat-window { flex-grow: 1; background-color: #f4f4f5; display: flex; flex-direction: column; }
.tg-chat-header { height: 56px; background-color: white; border-bottom: 1px solid #dfe1e5; display: flex; align-items: center; padding: 0 20px; z-index: 10; }
.chat-header-user { display: flex; flex-direction: column; }
.chat-status { font-size: 0.8rem; color: #707579; }
.tg-chat-messages { flex-grow: 1; overflow-y: auto; padding: 20px 40px; display: flex; flex-direction: column; gap: 12px; }
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
.tg-edit-sidebar { width: 360px; background-color: white; border-left: 1px solid #dfe1e5; display: flex; flex-direction: column; }
.sidebar-block-title { height: 56px; display: flex; align-items: center; padding: 0 20px; font-weight: 600; border-bottom: 1px solid #dfe1e5; color: #3390ec; }
.edit-form { padding: 20px; display: flex; flex-direction: column; gap: 20px; overflow-y: auto; }
.form-group { display: flex; flex-direction: column; gap: 8px; }
.form-group label { font-size: 0.85rem; color: #707579; font-weight: 500; }
.form-group textarea { background-color: #f4f4f5; border: 1px solid #dfe1e5; color: #1a1a1a; padding: 10px; border-radius: 6px; font-family: inherit; font-size: 0.9rem; resize: vertical; }
.form-group textarea:focus { outline: none; border-color: #3390ec; background-color: white; }
.tg-btn { padding: 11px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: background-color 0.15s; font-size: 0.9rem; }
.tg-btn-success { background-color: #3390ec; color: white; }
.tg-btn-success:hover { background-color: #2b7cc8; }
.tg-no-chat-selected { flex-grow: 1; display: flex; justify-content: center; align-items: center; background-color: #f4f4f5; }
.tg-select-hint { background-color: rgba(255, 255, 255, 0.9); padding: 8px 18px; border-radius: 15px; font-size: 0.9rem; color: #707579; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }
.tg-empty-txt { text-align: center; color: #a1aab3; font-size: 0.9rem; margin-top: 20px; font-style: italic; }
</style>