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
          <img class="avatar" src="./mentor.png" :alt="chat.name" />
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
            <img class="avatar-large" src="./mentor.png" :alt="selectedChat.name" />
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
          <aside v-if="suggestionsPanelOpen" class="suggestions-panel">
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
            <!-- Изображения над текстом -->
            <div v-if="msg.images && msg.images.length" class="msg-images">
              <img
                v-for="(imgSrc, idx) in msg.images"
                :key="idx"
                :src="imgSrc"
                alt="attachment"
                class="msg-image"
                @load="scrollToBottom"
              />
            </div>
            <!-- Текст (только если не пустой) -->
            <div v-if="msg.text" class="msg-text">{{ msg.text }}</div>
            <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
          </div>
          <!-- Индикатор ожидания ответа ИИ -->
          <div v-if="waitingAI" class="message received typing-indicator">
            <div class="dots">
              <span></span><span></span><span></span>
            </div>
            <div class="msg-time">...</div>
          </div>
        </div>

        <div v-if="selectedChat && selectedChat.is_main === true" class="analyze-bar">
          <button
            :class="['analyze-toggle', analyzeMode && 'active']"
            @click="toggleAnalyzeMode"
            :title="analyzeMode ? 'Режим анализа анкеты включён' : 'Нажмите чтобы включить режим анализа анкеты'"
          >
            Анализ анкеты
          </button>

          <button
            :class="['analyze-toggle', photoFeedbackMode && 'active']"
            @click="togglePhotoFeedbackMode"
            :title="photoFeedbackMode ? 'Режим отзыва о фото включён' : 'Нажмите чтобы отправить фото на отзыв'"
          >
            Отзыв о фото
          </button>
        </div>
        <!-- Input Area -->
        <div class="input-bar">
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="hidden-file-input"
            @change="onImageSelected"
            multiple
          />

          <button class="icon attach" @click="triggerFileSelect" title="Прикрепить изображение">
            📎
          </button>

            <div v-if="attachedImages.length" class="thumbs">
              <div
                v-for="(img, idx) in attachedImages"
                :key="img.id"
                class="thumb"
                :title="img.file.name"
              >
                <img :src="img.preview" alt="preview" />
                <button class="remove" @click="removeImage(idx)" title="Удалить">×</button>
              </div>
            </div>

          <input
            type="text"
            v-model="newMessage"
            placeholder="Введите сообщение..."
            @keyup.enter="sendMessage"
          />

          <button class="icon send" @click="sendMessage" title="Отправить">
            <svg class="icon-plane" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M3 11.5 21 3l-6.5 18-3.5-6-6-3.5Z"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linejoin="round"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </div>
      <div v-else class="no-selection">Выберите чат слева</div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onBeforeUnmount } from 'vue'
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

// Realtime related
const pollingIntervalMs = 3500 // базовый интервал фонового опроса
let pollingTimer = null
let focused = true
const waitingAI = ref(false) // показываем индикатор пока ждём ответа
let lastMessageIds = new Map() // chat.id -> last message id (для быстрой проверки)

// Fallback avatar (40x40 placeholder)
const placeholderAvatar = './mentor.png'

/* ====== SUGGESTIONS STATE ====== */
const suggestionsPanelOpen = ref(false)
const suggestionsLoading = ref(false)
const suggestionsError = ref('')
const suggestionsList = ref([])

const analyzeMode = ref(false)
const photoFeedbackMode = ref(false) // Новый режим отправки фото на /photo

// Кэш по chat.id, чтобы не перезагружать без необходимости
const suggestionsCache = new Map()
const fileInput = ref(null)
const attachedImages = ref([])

/* =====================
 * HELPERS: TOKEN
 * ===================== */
const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}

/* =====================
 * REALTIME (Polling) IMPLEMENTATION
 * ===================== */
function startGlobalPolling() {
  stopGlobalPolling()
  pollingTimer = setInterval(async () => {
    if (!selectedChat.value) return
    try {
      await incrementalFetch(selectedChat.value)
    } catch (e) {
      // игнорируем единичные ошибки
    }
  }, pollingIntervalMs)
}

function stopGlobalPolling() {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

async function incrementalFetch(chat) {
  if (!chat) return
  const prevLastId = lastMessageIds.get(chat.id)
  const token = getToken()
  const { data } = await axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message/get_messages_from_chat/${chat.id}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const normalized = (data || []).map(m => ({
    id: m.id,
    text: m.text,
    date: m.date,
    created_at: m.created_at || m.date,
    is_user: m.is_user,
    images: m.images || m.image_urls || []
  }))

  const newLastId = normalized.at(-1)?.id
  if (newLastId && newLastId !== prevLastId) {
    chat.messages = normalized
    lastMessageIds.set(chat.id, newLastId)
    await nextTick()
    scrollToBottom()
    if (waitingAI.value) {
      const last = normalized.at(-1)
      if (last && !last.is_user) {
        waitingAI.value = false
      }
    }
  }
}

function handleVisibilityChange() {
  focused = !document.hidden
  if (focused) {
    if (selectedChat.value) incrementalFetch(selectedChat.value)
  }
}

/* =====================
 * INSERT SUGGESTION
 * ===================== */
function insertSuggestion(s) {
  const txt = s.text || s.message || (typeof s === 'string' ? s : '')
  if (!txt) return
  if (newMessage.value) {
    newMessage.value = newMessage.value.trimEnd() + (newMessage.value.endsWith(' ') ? '' : ' ') + txt
  } else {
    newMessage.value = txt
  }
  requestAnimationFrame(() => {})
}

function triggerFileSelect() {
  if (!fileInput.value) return
  fileInput.value.click()
}

function onImageSelected(e) {
  const files = Array.from(e.target.files || [])
  const images = files.filter(f => f.type.startsWith('image/'))
  images.forEach(f => {
    attachedImages.value.push({
      id: `${Date.now()}-${Math.random()}`,
      file: f,
      preview: URL.createObjectURL(f),
    })
  })
  e.target.value = ''
}

function removeImage(index) {
  const [removed] = attachedImages.value.splice(index, 1)
  if (removed && removed.preview) {
    URL.revokeObjectURL(removed.preview)
  }
}

function clearAttachedImages() {
  // Не отзываем blob URL немедленно, чтобы оптимистичное сообщение могло их показать
  attachedImages.value = []
}

function toggleSuggestionsPanel() {
  if (!selectedChat.value) return
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

/* =====================
 * FETCH CHATS
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
      await openChat(main)
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
    const at = a.messages.at(-1)?.created_at || ''
    const bt = b.messages.at(-1)?.created_at || ''
    return bt.localeCompare(at)
  })
}

async function fetchMessages(chat) {
  if (!chat || chat.loading_messages) return
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
      created_at: m.created_at || m.date,
      is_user: m.is_user,
      images: m.images || m.image_urls || []
    }))
    chat.messages_loaded = true
    const last = chat.messages.at(-1)
    if (last) lastMessageIds.set(chat.id, last.id)
    sortChats()
    await nextTick()
    scrollToBottom()
  } catch (e) {
    console.error('Ошибка загрузки сообщений', e)
  } finally {
    chat.loading_messages = false
  }
}

async function openChat(chat) {
  selectedChat.value = chat
  suggestionsPanelOpen.value = false
  await fetchMessages(chat)
  incrementalFetch(chat)
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
  const hasImages = attachedImages.value.length > 0
  if (!chat) return
  if (!text && !hasImages) return

  const optimistic = {
    local_id: Date.now(),
    text: text || (hasImages ? '' : ''),
    created_at: new Date().toISOString(),
    is_user: true,
    pending: true,
    has_images: hasImages,
    images_count: attachedImages.value.length,
    images: hasImages ? attachedImages.value.map(i => i.preview) : []
  }
  chat.messages.push(optimistic)
  newMessage.value = ''
  await nextTick()
  scrollToBottom()

  try {
    const token = getToken()
    const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/message`
    let endpoint
    let payload
    let config = {
      headers: { Authorization: `Bearer ${token}` },
    }

    const mainChat = chat.is_main === true

    if (photoFeedbackMode.value && !hasImages) {
      optimistic.error = true
      optimistic.text = 'Для "Отзыв о фото" нужно прикрепить хотя бы одно изображение.'
      return
    }

    if (mainChat) {
      if (photoFeedbackMode.value && hasImages) {
        endpoint = `${base}/photo`
        payload = new FormData()
        if (text) payload.append('text', text)
        attachedImages.value.forEach(({ file }) => {
          payload.append('image', file)
        })
      } else if (hasImages) {
        endpoint = `${base}/chat_with_screenshot`
        payload = new FormData()
        payload.append('chat_id', chat.id)
        if (text) payload.append('text', text)
        if (attachedImages.value.length === 1) {
          payload.append('image', attachedImages.value[0].file)
        } else {
          attachedImages.value.forEach(fObj => {
            payload.append('images[]', fObj.file)
          })
        }
        config.headers['Content-Type'] = 'multipart/form-data'
      } else {
        if (analyzeMode.value) {
          endpoint = `${base}/form`
        } else {
          endpoint = `${base}/send`
        }
        payload = { chat_id: chat.id, text }
      }
    } else {
      endpoint = `${base}/send_partner`
      payload = { chat_id: chat.id, text }
    }

    if (analyzeMode.value) analyzeMode.value = false
    if (photoFeedbackMode.value) photoFeedbackMode.value = false

    waitingAI.value = mainChat

    const { data } = await axios.post(endpoint, payload, config)

    optimistic.id = data.id
    optimistic.created_at = data.created_at || optimistic.created_at
    if (data.images && Array.isArray(data.images)) {
      optimistic.images = data.images
    }
    optimistic.pending = false
    quickPollForAIReply(chat)
  } catch (e) {
    optimistic.error = true
    waitingAI.value = false
    console.error('Не удалось отправить сообщение', e)
  } finally {
    if (hasImages) {
      clearAttachedImages()
    }
  }
}

/* =====================
 * ACTIVE WAIT LOOP
 * ===================== */
async function quickPollForAIReply(chat) {
  const maxDurationMs = 20000
  const stepMs = 1500
  const start = performance.now()
  while (waitingAI.value && performance.now() - start < maxDurationMs) {
    await incrementalFetch(chat)
    if (!waitingAI.value) break
    await new Promise(r => setTimeout(r, stepMs))
  }
}

function toggleAnalyzeMode() {
  if (!analyzeMode.value) {
    photoFeedbackMode.value = false
  }
  analyzeMode.value = !analyzeMode.value
}

function togglePhotoFeedbackMode() {
  if (!photoFeedbackMode.value) {
    analyzeMode.value = false
  }
  photoFeedbackMode.value = !photoFeedbackMode.value
}

function retryMessage(msg) {
  if (!msg.error) return
  // TODO: реализовать повторную отправку
}
function attach() {}
function toggleMenu() {}

/* =====================
 * LIFECYCLE
 * ===================== */
onMounted(async () => {
  await fetchChats()
  startGlobalPolling()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  stopGlobalPolling()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  attachedImages.value.forEach(i => i.preview && URL.revokeObjectURL(i.preview))
})
</script>

<style scoped>
.chat-app { display: flex; height: 100vh; font-family: sans-serif; }
.sidebar { width: 300px; border-right: 1px solid #ddd; display: flex; flex-direction: column; min-height: 0; }
.menu-bar { display: flex; align-items: center; padding: 10px; flex: 0 0 auto; }
.hamburger { background: none; border: none; font-size: 1.5rem; cursor: pointer; }
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
.chat-window { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.chat-container { flex: 1; display: flex; flex-direction: column; min-height: 0; height: 100%; }
.chat-header { display: flex; align-items: center; justify-content: space-between; padding: 10px; border-bottom: 1px solid #ddd; flex: 0 0 auto; background: #fff; z-index: 6; }
.avatar-large { width: 50px; height: 50px; border-radius: 50%; margin-right: 10px; object-fit: cover; }
.messages { flex: 1 1 auto; padding: 10px; overflow-y: auto; background: #f9f9f9; display: flex; flex-direction: column; gap: 8px; min-height: 0; scroll-behavior: smooth; }
.message { max-width: 70%; padding: 8px 10px; border-radius: 10px; position: relative; display: flex; flex-direction: column; gap: 4px; }
.message .msg-text { word-wrap: break-word; }
.message .msg-time { font-size: 0.65rem; opacity: 0.7; align-self: flex-end; }
.sent { background: #4caf50; color: white; margin-left: auto; }
.received { background: white; border: 1px solid #ccc; margin-right: auto; }
.input-bar { flex: 0 0 auto; position: sticky; bottom: 0; background: #fff; z-index: 5; display: flex; align-items: center; padding: 10px; gap: 8px; border-top: 1px solid #ddd; }
.input-bar .icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; }
.input-bar input { flex: 1; padding: 8px 14px; border: 1px solid #ccc; border-radius: 20px; }
.no-selection { display: flex; align-items: center; justify-content: center; flex: 1; font-size: 1rem; color: #666; }
@media (max-width: 600px) { .sidebar { width: 220px; } .chat-last { max-width: 100px; } }
.icon-plane { width: 20px; height: 20px; display: block; }
.analyze-bar { padding: 6px 10px 0 10px; background: #fff; border-top: 1px solid #eee; }
.analyze-toggle { cursor: pointer; background: #f2f2f2; border: 1px solid #ccc; border-radius: 16px; padding: 6px 14px; font-size: 0.8rem; letter-spacing: .5px; text-transform: uppercase; font-weight: 600; transition: background .15s, border-color .15s, color .15s; }
.analyze-toggle.active { background: #4caf50; color: #fff; border-color: #4caf50; }
.analyze-toggle:not(.active):hover { background: #e6e6e6; }
.chat-header-actions { display: flex; align-items: center; }
.suggest-btn { background: #1976d2; color: #fff; border: 1px solid #1565c0; border-radius: 18px; padding: 6px 14px; font-size: 0.75rem; font-weight: 600; letter-spacing: .5px; cursor: pointer; transition: background .2s, box-shadow .2s; }
.suggest-btn:hover:not(:disabled) { background: #1565c0; }
.suggest-btn:disabled { opacity: 0.6; cursor: default; }
.suggestions-panel { position: absolute; top: 60px; right: 0; width: 300px; height: calc(100% - 60px); background: #ffffff; border-left: 1px solid #ddd; box-shadow: -2px 0 6px rgba(0,0,0,0.05); display: flex; flex-direction: column; z-index: 20; }
.panel-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid #eee; background: #f7f7f7; }
.panel-header h3 { margin: 0; font-size: 0.95rem; font-weight: 600; }
.close-x { background: none; border: none; font-size: 1.2rem; line-height: 1; cursor: pointer; padding: 4px 8px; }
.panel-body { padding: 10px 12px; overflow-y: auto; font-size: 0.85rem; line-height: 1.3; flex: 1; }
.panel-body.state { display: flex; flex-direction: column; gap: 10px; color: #555; font-size: 0.85rem; justify-content: flex-start; }
.panel-body.state.error { color: #c62828; }
.retry { align-self: flex-start; background: #c62828; color: #fff; border: none; border-radius: 14px; padding: 4px 10px; cursor: pointer; font-size: 0.7rem; }
.suggestions-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.suggestion-item { border: 1px solid #e2e2e2; background: #fafafa; border-radius: 8px; padding: 8px 10px; display: flex; flex-direction: column; gap: 6px; }
.suggestion-text { white-space: pre-wrap; word-break: break-word; font-size: 0.8rem; }
.suggestion-actions { display: flex; justify-content: flex-end; }
.suggestion-actions button { background: #4caf50; color: #fff; border: none; font-size: 0.7rem; padding: 4px 10px; border-radius: 14px; cursor: pointer; transition: background .15s; }
.suggestion-actions button:hover { background: #449b48; }
.slide-left-enter-active, .slide-left-leave-active { transition: transform .25s ease, opacity .25s ease; }
.slide-left-enter-from, .slide-left-leave-to { transform: translateX(100%); opacity: 0; }
.hidden-file-input { display: none; }
.thumbs { display: flex; gap: 6px; max-width: 240px; overflow-x: auto; padding: 2px 4px; }
.thumb { position: relative; width: 46px; height: 46px; border: 1px solid #ccc; border-radius: 6px; overflow: hidden; flex: 0 0 auto; background: #fff; }
.thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb .remove { position: absolute; top: -6px; right: -6px; background: #e53935; color: #fff; border: none; font-size: 0.65rem; width: 18px; height: 18px; border-radius: 50%; cursor: pointer; line-height: 18px; padding: 0; }
/* Typing indicator */
typing-indicator { display: flex; align-items: center; gap: 6px; }
.dots { display: inline-flex; gap: 4px; }
.dots span { width: 6px; height: 6px; background: #ccc; border-radius: 50%; display: inline-block; animation: blink 1s infinite ease-in-out; }
.dots span:nth-child(2) { animation-delay: .2s; }
.dots span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 0%, 80%, 100% { opacity: .2 } 40% { opacity: 1 } }

/* Новые стили для изображений сообщений */
.msg-images { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:4px; max-width:100%; }
.msg-image { display:block; width:120px; height:120px; object-fit:cover; border-radius:8px; border:1px solid #ddd; background:#fff; }
.sent .msg-images .msg-image { border-color: rgba(255,255,255,0.5); }
</style>
