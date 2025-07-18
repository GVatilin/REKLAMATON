<template>
  <div class="chat-app">
    <aside class="sidebar">
      <!-- Menu and Tabs -->
      <div class="menu-bar">
        <button class="hamburger">☰</button>
        <div class="tabs">
          <button :class="['tab', activeTab === 'chats' && 'active']" @click="activeTab = 'chats'">Чаты</button>
          <button :class="['tab', activeTab === 'requests' && 'active']" @click="activeTab = 'requests'">Запросы</button>
        </div>
      </div>

      <!-- Search -->
      <input type="text" class="search" placeholder="Search..." v-model="searchQuery" />

      <!-- Chats List -->
      <ul class="chat-list">
        <!-- Mentor pinned on top -->
        <li
          class="chat-item"
          :class="{ active: selectedChat.id === mentor.id }"
          @click="openChat(mentor)"
        >
          <img class="avatar" :src="mentor.avatar" alt="Mentor" />
          <div class="chat-info">
            <div class="chat-name">{{ mentor.name }}</div>
            <div class="chat-last">{{ lastMessage(mentor) }}</div>
          </div>
          <div class="chat-time">{{ lastTime(mentor) }}</div>
        </li>

        <!-- Partner chats -->
        <li
          v-for="chat in filteredPartners"
          :key="chat.id"
          class="chat-item"
          :class="{ active: selectedChat.id === chat.id }"
          @click="openChat(chat)"
        >
          <img class="avatar" :src="chat.avatar" :alt="chat.name" />
          <div class="chat-info">
            <div class="chat-name">{{ chat.name }}</div>
            <div class="chat-last">{{ lastMessage(chat) }}</div>
          </div>
          <div class="chat-time">{{ lastTime(chat) }}</div>
        </li>
      </ul>
    </aside>

    <!-- Main Chat Window -->
    <main class="chat-window">
      <div v-if="selectedChat" class="chat-container">
        <!-- Chat Header -->
        <div class="chat-header">
          <img class="avatar-large" :src="selectedChat.avatar" :alt="selectedChat.name" />
          <h2>{{ selectedChat.name }}</h2>
        </div>

        <!-- Messages -->
        <div class="messages">
          <div
            v-for="msg in selectedChat.messages"
            :key="msg.id"
            class="message"
            :class="msg.from === 'me' ? 'sent' : 'received'"
          >
            {{ msg.text }}
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-bar">
          <button class="icon attach">📎</button>
          <input
            type="text"
            v-model="newMessage"
            placeholder="Введите сообщение..."
            @keyup.enter="sendMessage"
          />
          <button class="icon mic">🎤</button>
          <button class="icon send" @click="sendMessage">✔️</button>
        </div>
      </div>
      <div v-else class="no-selection">Выберите чат слева</div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Active tab state
const activeTab = ref('chats')

// Search query
const searchQuery = ref('')

// Mentor chat (always pinned)
const mentor = {
  id: 'mentor',
  name: 'Ментор',
  avatar: 'https://via.placeholder.com/40',
  messages: [
    { id: 1, from: 'mentor', text: 'Hey, what\'s up?', time: '14:15' }
  ]
}

// Example partner chats
const partners = ref([
  {
    id: 'alex',
    name: 'Александра',
    avatar: 'https://via.placeholder.com/40',
    messages: [
      { id: 1, from: 'partner', text: 'Привет!', time: '14:15' }
    ]
  },
  // добавить другие чаты здесь
])

// Currently selected chat
const selectedChat = ref(mentor)
const newMessage = ref('')

// Filter partners by search query
const filteredPartners = computed(() => {
  return partners.value.filter(c =>
    c.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

// Open a chat
function openChat(chat) {
  selectedChat.value = chat
}

// Send a new message
function sendMessage() {
  if (!newMessage.value.trim()) return

  selectedChat.value.messages.push({
    id: Date.now(),
    from: 'me',
    text: newMessage.value.trim(),
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  newMessage.value = ''
}

// Helpers
function lastMessage(chat) {
  const msgs = chat.messages
  return msgs.length ? msgs[msgs.length - 1].text : ''
}

function lastTime(chat) {
  const msgs = chat.messages
  return msgs.length ? msgs[msgs.length - 1].time : ''
}
</script>

<style scoped>
.chat-app {
  display: flex;
  height: 100vh;
  font-family: sans-serif;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.menu-bar {
  display: flex;
  align-items: center;
  padding: 10px;
}
.hamburger {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.tabs {
  display: flex;
  margin-left: 10px;
}
.tab {
  flex: 1;
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
}
.tab.active {
  border-bottom: 2px solid #333;
}
.search {
  margin: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  margin: 0;
  list-style: none;
}
.chat-item {
  display: flex;
  align-items: center;
  padding: 10px;
  cursor: pointer;
}
.chat-item.active {
  background: #e6ffe6;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
}
.chat-info {
  flex: 1;
}
.chat-name {
  font-weight: bold;
}
.chat-last {
  font-size: 0.9rem;
  color: #666;
}
.chat-time {
  font-size: 0.8rem;
  color: #999;
}

.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.chat-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ddd;
}
.avatar-large {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  margin-right: 10px;
}
.messages {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  background: #f9f9f9;
}
.message {
  max-width: 60%;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 8px;
}
.sent {
  background: #4caf50;
  color: white;
  align-self: flex-end;
}
.received {
  background: white;
  border: 1px solid #ccc;
  align-self: flex-start;
}
.input-bar {
  display: flex;
  align-items: center;
  padding: 10px;
  border-top: 1px solid #ddd;
}
.input-bar .icon {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  margin-right: 8px;
}
.input-bar input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 20px;
  margin-right: 8px;
}
</style>
