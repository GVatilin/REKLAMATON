<script setup>
import axios from "axios";
import { ref, onMounted, watch } from "vue";
import NavBar from "../../components/light_style/NavBar.vue";
import invalidUserPanel from "../../components/NotRegisteredLight.vue"

document.body.style.overflowY = 'hidden';

const user = ref({ username: "Loading..." });
const settings = ref(null);

const editingText = ref(false);
const textInput = ref("");

const workingStart = ref("");
const workingEnd = ref("");

// Функция для получения токена
function getToken() {
  const token = localStorage.getItem("chronoJWTToken");
  if (!token) {
    throw new Error("Token is missing. Please log in.");
  }
  return token;
}

// Получение данных пользователя
async function getUser() {
  try {
    const token = getToken();
        if (token == null) {
          return -1
        }
    const response = await axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
      return -1
  }
}

async function fetchUser() {
  user.value = await getUser()
}

// Получение настроек
async function fetchSettings() {
  try {
    const token = getToken();
    const response = await axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/get_user_settings`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    settings.value = response.data;
  } catch (error) {
    console.error("Error fetching settings:", error)
  }
}

function formatTime(time) {
  // Предполагается, что время приходит в виде "08:00:00"
  return time.slice(0, 5);
}

// Обновление локальных переменных при получении настроек
watch(settings, (newSettings) => {
  if(newSettings){
    textInput.value = newSettings.text_settings || "";
    workingStart.value = newSettings.start_working ? formatTime(newSettings.start_working) : "";
    workingEnd.value = newSettings.end_working ? formatTime(newSettings.end_working) : "";
  }
});

// Функция для отправки текстовых настроек с передачей введённого значения
async function setTextSettings(newText) {
  try {
    const token = getToken();
    await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/add_text_settings`, 
      { text: newText },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    await fetchSettings();
  } catch (error) {
    console.error("Error set text settings:", error)
  }
}

// Функция для отправки рабочего времени с передачей начала и конца
async function setWorkingHours(start, end) {
  try {
    const token = getToken();
    await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/set_working_hours`, 
      { start_working: start, end_working: end },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    await fetchSettings();
  } catch (error) {
    console.error("Error set working hours:", error)
  }
}

// Сохранение текстовых настроек
function saveTextSettings() {
  setTextSettings(textInput.value);
  editingText.value = false;
}

// Сохранение рабочего времени
function saveWorkingHours() {
  setWorkingHours(workingStart.value, workingEnd.value);
}

onMounted(async () => {
  await fetchUser();
  await fetchSettings();
});
</script>

<template>
  <div class="page-container">
    <invalidUserPanel v-show="user == -1"/>
    
    <!-- Навигационная панель слева -->
    <div class="nav-container">
      <NavBar :username="user.username" />
    </div>

    <!-- Настройки справа -->
    <div class="settings-container">
      <!-- Секция для текстовых настроек генерации -->
      <div class="text-settings">
        <h3>Текстовые настройки генерации</h3>
        <div v-if="settings">
          <div v-if="!editingText">
            <div class="text-box">{{ settings.text_settings || "Нет настроек" }}</div>
            <div class="button-container">
              <button class="btn btn-small" @click="editingText = true">Изменить</button>
            </div>
          </div>
          <div v-else>
            <textarea
              v-model="textInput"
              class="text-box"
              placeholder="Введите текстовые настройки"
            ></textarea>
            <div class="button-container">
              <button class="btn btn-small" @click="saveTextSettings">Сохранить</button>
              <button class="btn btn-cancel btn-small" @click="editingText = false">
                Отмена
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Секция для установки рабочего времени -->
      <div class="working-hours" v-if="settings">
        <h3>Рабочее время</h3>
        <div class="time-form">
          <label>
            Начало:
            <input type="time" v-model="workingStart" class="time-input" />
          </label>
          <label>
            Конец:
            <input type="time" v-model="workingEnd" class="time-input" />
          </label>
        </div>
        <div class="button-container">
          <button class="btn btn-small" @click="saveWorkingHours">Сохранить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');

.page-container {
  display: flex;
  flex-direction: row;
  background: #f7f9fc;
  font-family: 'Inter', sans-serif;
  height: 100vh;
}

/* Контейнер для настроек справа */
.settings-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  font-size: 1rem;
}

/* Стили для секций настроек */
.text-settings,
.working-hours {
  background: #fff;
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 8px;
  width: 40%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
}

h3 {
  text-align: left;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
  font-weight: 700;
  color: #838385;
}

.text-box,
textarea.text-box {
  width: 100%;
  height: 200px; /* фиксированная высота */
  margin: 0; /* убраны внешние отступы */
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 12px;
  box-sizing: border-box;
  overflow-y: auto;
  font-size: 0.95rem;
  font-family: 'Inter', sans-serif;
  text-align: left;
  vertical-align: top;
  line-height: 1.5;
  margin-bottom: 0.8rem;
}

/* Дополнительное правило для textarea */
textarea.text-box {
  resize: none;
}
/*
.text-box {
  width: 100%;
  height: 200px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 12px;
  text-align: left;
  display: block;
  margin-bottom: 0.8rem;
  box-sizing: border-box;
  overflow-y: auto;
  font-size: 1rem;
}


textarea.text-box {
  width: 100%;
  height: 200px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 12px;
  text-align: left;
  font-size: 16px;
  box-sizing: border-box;
  resize: none;
  overflow-y: auto;
  font-size: 1rem;
}
*/
.text-box::-webkit-scrollbar {
  width: 8px;
}

.text-box::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.text-box::-webkit-scrollbar-thumb {
  background: #cacaca;
  border-radius: 4px;
}

.text-box::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.time-form {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.time-form label {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-size: 1rem;
}

.time-input {
  width: calc(100% - 20px);
  padding: 10px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

.button-container {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  background-color: #4285F4;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.2s;
}

.btn:hover {
  background-color: #2980b9;
}

.btn-cancel {
  background-color: #e74c3c;
}

.btn-cancel:hover {
  background-color: #c0392b;
}

.btn-small {
  width: 6rem;
  height: 2.2rem;
  font-size: 14px;
  border-radius: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: -0.15rem;
  margin-left: 0.6rem;
}

.text-box,
textarea.text-box {
  font-family: 'Inter', sans-serif;
}
</style>
