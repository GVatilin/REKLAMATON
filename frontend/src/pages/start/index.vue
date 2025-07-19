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
              <span v-if="chat.is_main" class="badge">ИИ помощник</span>
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
          <div class="chat-header-left">
            <img class="avatar-large" :src="selectedChat.avatar || placeholderAvatar" :alt="selectedChat.name" />
            <h2>{{ selectedChat.name }}</h2>
          </div>

          <!-- Кнопка подсказок только для НЕ-мейн чатов -->
          <div v-if="selectedChat && !selectedChat.is_main" class="chat-header-actions">
            <button
              class="suggest-btn"
              :disabled="suggestionsLoading"
              @click="toggleSuggestionsPanel"
              :title="suggestionsPanelOpen ? 'Скрыть предложения' : 'Получить предложения сообщений'"
            >
              <span v-if="!suggestionsLoading">
                {{ suggestionsPanelOpen ? 'Скрыть' : 'Предложить сообщения' }}
              </span>
              <span v-else>Загрузка…</span>
            </button>
          </div>
        </div>

        <!-- Панель предложений (справа) -->
        <transition name="slide-left">
          <aside
            v-if="suggestionsPanelOpen"
            class="suggestions-panel"
          >
            <div class="panel-header">
              <h3>Предложения</h3>
              <button class="close-x" @click="toggleSuggestionsPanel" title="Закрыть">×</button>
            </div>

            <div class="panel-body" v-if="!suggestionsLoading && !suggestionsError && suggestionsList.length">
              <ul class="suggestions-list">
                <li
                  v-for="(s, i) in suggestionsList"
                  :key="s.id || i"
                  class="suggestion-item"
                >
                  <div class="suggestion-text">{{ s.text || s.message || s }}</div>
                  <div class="suggestion-actions">
                    <button @click="insertSuggestion(s)">Вставить</button>
                  </div>
                </li>
              </ul>
            </div>

            <div class="panel-body state" v-else-if="suggestionsLoading">
              Загрузка предложений...
            </div>
            <div class="panel-body state error" v-else-if="suggestionsError">
              {{ suggestionsError }}
              <button class="retry" @click="fetchSuggestions(selectedChat)">Повторить</button>
            </div>
            <div class="panel-body state" v-else>
              Нет предложений
            </div>
          </aside>
        </transition>

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

        <!-- Analyze Toggle (only for mentor chat 'Анализ анкеты') -->
        <div v-if="selectedChat && selectedChat.is_main === true" class="analyze-bar">
          <button :class="['analyze-toggle', analyzeMode && 'active']"
                  @click="toggleAnalyzeMode"
                  :title="analyzeMode ? 'Режим анализа включён' : 'Нажмите чтобы включить режим анализа'">
            Анализ анкеты
          </button>
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
          <button class="icon send" @click="sendMessage" title="Отправить">
            <svg class="icon-plane" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M3 11.5 21 3l-6.5 18-3.5-6-6-3.5Z"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linejoin="round"
                    stroke-linecap="round" />
            </svg>
          </button>
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
const analyzeMode = ref(false) // toggle for special analyze sending

// Fallback avatar (40x40 placeholder)
const placeholderAvatar = 'https://via.placeholder.com/40'

/* ====== SUGGESTIONS STATE ====== */
const suggestionsPanelOpen = ref(false)
const suggestionsLoading = ref(false)
const suggestionsError = ref('')
const suggestionsList = ref([])

// Кэш по chat.id, чтобы не перезагружать без необходимости
const suggestionsCache = new Map()

function toggleSuggestionsPanel() {
  if (!selectedChat.value) return
  // Если открываем – и нет кэша или кэш пустой — загрузим
  if (!suggestionsPanelOpen.value) {
    openSuggestionsFor(selectedChat.value)
  } else {
    suggestionsPanelOpen.value = false
  }
}

function openSuggestionsFor(chat) {
  suggestionsPanelOpen.value = true
  if (suggestionsCache.has(chat.id)) {
    suggestionsList.value = suggestionsCache.get(chat.id)
    return
  }
  fetchSuggestions(chat)
}

async function fetchSuggestions(chat) {
  if (!chat) return
  suggestionsLoading.value = true
  suggestionsError.value = ''
  suggestionsList.value = []
  try {
    const token = getToken()
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message/chat_analysis/${chat.id}`,
      { headers: { Authorization: `Bearer ${token}` } },
    )

    const normalized = Array.isArray(data)
      ? data.map(item => {
          if (typeof item === 'string') return { text: item }
          if (item && typeof item === 'object') {
            // поддерживаем варианты ключей
            return { id: item.id, text: item.text || item.message || JSON.stringify(item) }
          }
          return { text: String(item) }
        })
      : []
    suggestionsList.value = normalized
    suggestionsCache.set(chat.id, normalized)
  } catch (e) {
    suggestionsError.value = e?.response?.data?.message || e.message || 'Не удалось получить предложения'
  } finally {
    suggestionsLoading.value = false
  }
}

function insertSuggestion(s) {
  // Вставим текст предложения в поле ввода (не сразу отправляем — пользователь может отредактировать)
  const txt = s.text || s.message || (typeof s === 'string' ? s : '')
  if (!txt) return
  if (newMessage.value) {
    newMessage.value = newMessage.value.trimEnd() + (newMessage.value.endsWith(' ') ? '' : ' ') + txt
  } else {
    newMessage.value = txt
  }
  // Фокус на input — через nextTick если нужно
  requestAnimationFrame(() => {
    // Можно поймать сам input через querySelector либо ref, если заведёте ref
  })
}

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
  suggestionsPanelOpen.value = false // закрываем при смене
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
  requestAnimationFrame(() => {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  })
}

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

    // Новая логика выбора эндпоинта:
    const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message`
    let endpoint
    if (chat.is_main) {
      // Мейн-чат: обычная отправка -> /send, режим анализа -> /form
      endpoint = analyzeMode.value ? `${base}/form` : `${base}/send`
    } else {
      // Обычный (партнёрский) чат всегда -> /send_partner
      endpoint = `${base}/send_partner`
    }

    const body = { chat_id: chat.id, text }

    // Сбросим режим анализа после отправки
    if (analyzeMode.value) analyzeMode.value = false

    const { data } = await axios.post(endpoint, body, {
      headers: { Authorization: `Bearer ${token}` },
    })

    optimistic.id = data.id
    optimistic.created_at = data.created_at || optimistic.created_at
    optimistic.pending = false
  } catch (e) {
    optimistic.error = true
    console.error('Не удалось отправить сообщение', e)
  }
}


function toggleAnalyzeMode() {
  analyzeMode.value = !analyzeMode.value
}

function retryMessage(msg) {
  if (!msg.error) return
  // реализовать повторную отправку
}

/* =====================
 * PLACEHOLDER HANDLERS
 * ===================== */
function attach() { /* Реализовать прикрепление файлов */ }
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
  min-height: 0; /* чтобы список чатов мог скроллиться при необходимости */
}
.menu-bar {
  display: flex;
  align-items: center;
  padding: 10px;
  flex: 0 0 auto;
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
.chat-list { flex: 1 1 auto; overflow-y: auto; padding: 0; margin: 0; list-style: none; }
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

/* ---- Основная область ---- */
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* важно */
}
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0; /* важно для внутреннего скролла */
  height: 100%;
}
.chat-header {
  display: flex;
  align-items: center;
  padding: 10px;
  border-bottom: 1px solid #ddd;
  flex: 0 0 auto;
  background: #fff;
  z-index: 6; /* чтобы оставалась над сообщениями при sticky input */
}
.avatar-large { width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; object-fit: cover; }

.messages {
  flex: 1 1 auto;
  padding: 10px;
  overflow-y: auto; /* внутренний скролл */
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0; /* критично */
  scroll-behavior: smooth;
}
.message { max-width: 70%; padding: 8px 10px; border-radius: 10px; position: relative; display: flex; flex-direction: column; gap: 4px; }
.message .msg-text { word-wrap: break-word; }
.message .msg-time { font-size: 0.65rem; opacity: 0.7; align-self: flex-end; }
.sent { background: #4caf50; color: white; margin-left: auto; }
.received { background: white; border: 1px solid #ccc; margin-right: auto; }

.input-bar {
  flex: 0 0 auto;
  position: sticky; /* прилипает к низу контейнера */
  bottom: 0;
  background: #fff;
  z-index: 5;
  display: flex;
  align-items: center;
  padding: 10px;
  gap: 8px;
  border-top: 1px solid #ddd;
}
.input-bar .icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.input-bar input { flex: 1; padding: 8px 14px; border: 1px solid #ccc; border-radius: 20px; }

.no-selection { display: flex; align-items: center; justify-content: center; flex: 1; font-size: 1rem; color: #666; }

/* Дополнительно: адаптация для очень маленьких экранов */
@media (max-width: 600px) {
  .sidebar { width: 220px; }
  .chat-last { max-width: 100px; }
}

.icon-plane { width: 20px; height: 20px; display: block; }


/* Analyze toggle */
.analyze-bar {
  padding: 6px 10px 0 10px;
  background: #fff;
  border-top: 1px solid #eee;
}
.analyze-toggle {
  cursor: pointer;
  background: #f2f2f2;
  border: 1px solid #ccc;
  border-radius: 16px;
  padding: 6px 14px;
  font-size: 0.8rem;
  letter-spacing: .5px;
  text-transform: uppercase;
  font-weight: 600;
  transition: background .15s, border-color .15s, color .15s;
}
.analyze-toggle.active {
  background: #4caf50;
  color: #fff;
  border-color: #4caf50;
}
.analyze-toggle:not(.active):hover {
  background: #e6e6e6;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between; /* добавлено для размещения кнопки справа */
  position: relative;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-header-actions {
  display: flex;
  align-items: center;
}

.suggest-btn {
  background: #1976d2;
  color: #fff;
  border: 1px solid #1565c0;
  border-radius: 18px;
  padding: 6px 14px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: .5px;
  cursor: pointer;
  transition: background .2s, box-shadow .2s;
}
.suggest-btn:hover:not(:disabled) {
  background: #1565c0;
}
.suggest-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.suggestions-panel {
  position: absolute;
  top: 60px; /* ниже header */
  right: 0;
  width: 300px;
  height: calc(100% - 60px);
  background: #ffffff;
  border-left: 1px solid #ddd;
  box-shadow: -2px 0 6px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  z-index: 20;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #eee;
  background: #f7f7f7;
}
.panel-header h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
}
.close-x {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  padding: 4px 8px;
}

.panel-body {
  padding: 10px 12px;
  overflow-y: auto;
  font-size: 0.85rem;
  line-height: 1.3;
  flex: 1;
}

.panel-body.state {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #555;
  font-size: 0.85rem;
  justify-content: flex-start;
}

.panel-body.state.error {
  color: #c62828;
}

.retry {
  align-self: flex-start;
  background: #c62828;
  color: #fff;
  border: none;
  border-radius: 14px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 0.7rem;
}

.suggestions-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.suggestion-item {
  border: 1px solid #e2e2e2;
  background: #fafafa;
  border-radius: 8px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.suggestion-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.8rem;
}

.suggestion-actions {
  display: flex;
  justify-content: flex-end;
}

.suggestion-actions button {
  background: #4caf50;
  color: #fff;
  border: none;
  font-size: 0.7rem;
  padding: 4px 10px;
  border-radius: 14px;
  cursor: pointer;
  transition: background .15s;
}
.suggestion-actions button:hover {
  background: #449b48;
}

/* Анимация появления панели */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform .25s ease, opacity .25s ease;
}
.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

</style>
