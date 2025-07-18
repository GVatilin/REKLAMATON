<template>
  <div class="chat-app">
    <aside class="sidebar">
      <!-- Menu and Tabs -->
      <div class="menu-bar">
        <button class="hamburger" @click="toggleMenu">☰</button>
        <div class="tabs">
          <button :class="['tab', activeTab === 'chats' && 'active']" @click="activeTab = 'chats'">Чаты</button>
          <button :class="['tab', activeTab === 'requests' && 'active']" @click="activeTab = 'requests'">Запросы</button>
        </div>
      </div>

      <!-- Search -->
      <input type="text" class="search" placeholder="Поиск..." v-model="searchQuery" />

      <!-- Chats List -->
      <ul class="chat-list" v-if="!loading && !error">
        <li
          v-for="chat in visibleChats"
          :key="chat.id"
          class="chat-item"
          :class="{ active: selectedChat && selectedChat.id === chat.id, main: chat.is_main }"
          @click="openChat(chat)"
        >
          <img class="avatar" :src="chat.avatar || placeholderAvatar" :alt="chat.name" />
          <div class="chat-info">
            <div class="chat-name">
              {{ chat.name }}
              <span v-if="chat.is_main" class="badge">MAIN</span>
            </div>
            <div class="chat-last">{{ lastMessageText(chat) }}</div>
          </div>
          <div class="chat-time">{{ lastMessageTime(chat) }}</div>
        </li>
      </ul>
      <div v-else-if="loading" class="state-msg">Загрузка чатов...</div>
      <div v-else-if="error" class="state-msg error">Ошибка: {{ error }} <button @click="fetchChats">Повторить</button></div>
    </aside>

    <!-- Main Chat Window -->
    <main class="chat-window">
      <div v-if="selectedChat" class="chat-container">
        <!-- Chat Header -->
        <div class="chat-header">
          <img class="avatar-large" :src="selectedChat.avatar || placeholderAvatar" :alt="selectedChat.name" />
          <h2>{{ selectedChat.name }}</h2>
        </div>

        <!-- Messages -->
        <div class="messages" ref="messagesEl">
          <div
            v-for="msg in selectedChat.messages"
            :key="msg.local_id || msg.id"
            class="message"
            :class="msg.is_user ? 'sent' : 'received'"
          >
            <div class="msg-text">{{ msg.text }}</div>
            <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-bar">
          <button class="icon attach" @click="attach">📎</button>
          <input
            type="text"
            v-model="newMessage"
            placeholder="Введите сообщение..."
            @keyup.enter="sendMessage"
          />
          <button class="icon mic" @click="voiceInput">🎤</button>
          <button class="icon send" @click="sendMessage">✔️</button>
        </div>
      </div>
      <div v-else class="no-selection">Выберите чат слева</div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'

/* =====================
 * STATE
 * ===================== */
const activeTab = ref('chats')
const searchQuery = ref('')
const chats = ref([]) // raw fetched chats (Chat model: id, name, is_main)
const selectedChat = ref(null)
const loading = ref(false)
const error = ref('')
const newMessage = ref('')
const messagesEl = ref(null)

// Fallback avatar (40x40 placeholder)
const placeholderAvatar = 'https://via.placeholder.com/40'

const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}
/* =====================
 * FETCH CHATS (использует модель Chat: id, name, is_main)
 * ===================== */
async function fetchChats() {
  loading.value = true
  error.value = ''
  try {
    const token = getToken()
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/chat/get_user_chats`,
      { headers: { Authorization: `Bearer ${token}` } },
    )

    chats.value = (data || []).map(c => ({
      ...c,
      messages: [],
      messages_loaded: false,
      loading_messages: false,
    }))

    sortChats()

    const main = chats.value.find(c => c.is_main)
    if (main) {
      await openChat(main) // автоматически загрузим сообщения главного чата
    }
  } catch (e) {
    error.value = e?.response?.data?.message || e.message || 'Не удалось загрузить'
  } finally {
    loading.value = false
  }
}

function sortChats() {
  chats.value.sort((a, b) => {
    if (a.is_main && !b.is_main) return -1
    if (!a.is_main && b.is_main) return 1
    // Дополнительно можно сортировать по времени последнего сообщения:
    const at = a.messages.at(-1)?.created_at || ''
    const bt = b.messages.at(-1)?.created_at || ''
    return bt.localeCompare(at)
  })
}

async function fetchMessages(chat) {
  if (!chat || chat.loading_messages || chat.messages_loaded) return
  chat.loading_messages = true
  try {
    const token = getToken()
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message/get_messages_from_chat/${chat.id}`,
      { headers: { Authorization: `Bearer ${token}` } },
    )

    chat.messages = (data || []).map(m => ({
      id: m.id,
      text: m.text,
      date: m.date,
      is_user: m.is_user,
    }))
    chat.messages_loaded = true
    sortChats()
    await nextTick()
    scrollToBottom()
  } catch (e) {
    // Локально помечаем ошибку (можно вывести тостером)
    console.error('Ошибка загрузки сообщений', e)
  } finally {
    chat.loading_messages = false
  }
}

// Текущий пользователь (нужно знать для from_user). Если backend возвращает id в профиле — получите его.
const currentUserId = ref(null)
async function fetchCurrentUserId() {
  try {
    const token = getToken()
    // Подставьте реальный эндпоинт получения текущего пользователя
    // const { data } = await axios.get(`http://${import.meta.env.VITE_BACKEND_URL}:8080/api/v1/user/me`, { headers: { Authorization: `Bearer ${token}` } })
    // currentUserId.value = data.id
  } catch (e) {
    console.warn('Не удалось получить id пользователя')
  }
}

/* =====================
 * COMPUTED
 * ===================== */
const visibleChats = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return chats.value
  return chats.value.filter(c => c.name && c.name.toLowerCase().includes(q))
})

/* =====================
 * UI / HELPERS
 * ===================== */
async function openChat(chat) {
  selectedChat.value = chat
  await fetchMessages(chat)
}

function lastMessage(chat) {
  return chat.messages.at(-1) || null
}

function lastMessageText(chat) {
  return lastMessage(chat)?.text || ''
}

function lastMessageTime(chat) {
  const lm = lastMessage(chat)
  return lm ? formatTime(lm.created_at) : ''
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ts
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  if (!messagesEl.value) return
  messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}

/* =====================
 * SENDING MESSAGE (пример локально + POST)
 * ===================== */
async function sendMessage() {
  const text = newMessage.value.trim()
  const chat = selectedChat.value
  if (!text || !chat) return

  const optimistic = {
    local_id: Date.now(),
    text,
    created_at: new Date().toISOString(),
    is_user: true,
    pending: true,
  }
  chat.messages.push(optimistic)
  newMessage.value = ''
  await nextTick()
  scrollToBottom()

  try {
    const token = getToken()
    const body = { chat_id: chat.id, text }
    const { data } = await axios.post(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message/send`,
      body,
      { headers: { Authorization: `Bearer ${token}` } },
    )
    // Предполагаем что backend возвращает сохранённое сообщение
    optimistic.id = data.id
    optimistic.created_at = data.created_at || optimistic.created_at
    optimistic.pending = false
  } catch (e) {
    // Маркируем ошибку
    optimistic.error = true
    console.error('Не удалось отправить сообщение', e)
  }
}

function retryMessage(msg) {
  if (!msg.error) return
  // Можно реализовать повторную отправку
}

/* =====================
 * PLACEHOLDER HANDLERS
 * ===================== */
function attach() { /* Реализовать прикрепление файлов */ }
function voiceInput() { /* Реализовать ввод голосом */ }
function toggleMenu() { /* Реализовать открытие бокового меню */ }

/* =====================
 * LIFECYCLE
 * ===================== */
onMounted(async () => {
  await fetchCurrentUserId()
  await fetchChats()
})
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
.tabs { display: flex; margin-left: 10px; }
.tab { flex: 1; padding: 8px; border: none; background: none; cursor: pointer; }
.tab.active { border-bottom: 2px solid #333; }
.search { margin: 10px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.chat-list { flex: 1; overflow-y: auto; padding: 0; margin: 0; list-style: none; }
.chat-item { display: flex; align-items: center; padding: 10px; cursor: pointer; transition: background .15s; border-left: 4px solid transparent; }
.chat-item:hover { background: #f2f2f2; }
.chat-item.active { background: #e6ffe6; }
.chat-item.main { border-left-color: #4caf50; }
.avatar { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; object-fit: cover; }
.chat-info { flex: 1; }
.chat-name { font-weight: bold; display: flex; align-items: center; gap: 6px; }
.badge { background: #4caf50; color: #fff; padding: 2px 6px; font-size: 0.65rem; border-radius: 4px; letter-spacing: .5px; }
.chat-last { font-size: 0.85rem; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px; }
.chat-time { font-size: 0.75rem; color: #999; }
.state-msg { padding: 20px; font-size: 0.9rem; }
.state-msg.error { color: #c62828; }
.chat-window { flex: 1; display: flex; flex-direction: column; }
.chat-header { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #ddd; }
.avatar-large { width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; object-fit: cover; }
.messages { flex: 1; padding: 10px; overflow-y: auto; background: #f9f9f9; display: flex; flex-direction: column; gap: 8px; }
.message { max-width: 70%; padding: 8px 10px; border-radius: 10px; position: relative; display: flex; flex-direction: column; gap: 4px; }
.message .msg-text { word-wrap: break-word; }
.message .msg-time { font-size: 0.65rem; opacity: 0.7; align-self: flex-end; }
.sent { background: #4caf50; color: white; margin-left: auto; }
.received { background: white; border: 1px solid #ccc; margin-right: auto; }
.input-bar { display: flex; align-items: center; padding: 10px; border-top: 1px solid #ddd; gap: 8px; }
.input-bar .icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.input-bar input { flex: 1; padding: 8px 14px; border: 1px solid #ccc; border-radius: 20px; }
.no-selection { display: flex; align-items: center; justify-content: center; flex: 1; font-size: 1rem; color: #666; }
</style>
