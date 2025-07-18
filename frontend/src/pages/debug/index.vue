<template>
  <div id="app" class="container">
    <!-- Заголовок -->
    <h1 class="title">Debug</h1>

    <!-- Кнопки для переключения -->
    <div class="button-group">
      <button
        v-for="(cfg, key) in config"
        :key="key"
        @click="activeComponent = key"
        :class="{ active: activeComponent === key }"
      >
        {{ cfg.title }}
      </button>
    </div>

    <!-- Таблица -->
    <div class="component-container">
      <DebugTable
        v-if="activeComponent"
        :endpoint="config[activeComponent].endpoint"
        :title="config[activeComponent].title"
      />
    </div>
  </div>
</template>

<script>
import DebugTable from './components/DebugTable.vue';

export default {
  name: 'DebugPage',
  components: { DebugTable },
  data() {
    return {
      activeComponent: 'users',
      config: {
        users: {
          title: 'Users',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/debug/users_table/`
        },
        questions: {
          title: 'Questions',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_questions`
        },
        settings: {
          title: 'Settings',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/get_settings_debug`
        },
        answers: {
          title: 'Answers',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/debug/get_answers`
        },
        chapters: {
          title: 'Chapters',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_chapters`
        },
        topics: {
          title: 'Topics',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_topics`
        },
        ai_questions: {
          title: 'AIQuestions',
          endpoint: `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/debug/get_ai_questions`
        },
      }
    };
  },
};
</script>

<style>
/* Основной контейнер */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start; /* Размещаем элементы сверху */
  min-height: 100vh;
  background: linear-gradient(135deg, #d7ccc8, #a1887f);
  font-family: 'Arial', sans-serif;
  color: #4e342e;
  padding: 20px;
}

/* Заголовок */
.title {
  font-size: 48px;
  font-weight: bold;
  color: #3e2723;
  text-transform: uppercase;
  margin-bottom: 20px;
  text-align: center;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

/* Группа кнопок */
.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px; /* Отступ от кнопок до таблицы */
}

/* Кнопки */
.button-group button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  background-color: #4e342e;
  color: #fff;
  transition: background-color 0.3s, transform 0.2s;
}

.button-group button:hover {
  background-color: #3e2723;
  transform: scale(1.05);
}

.button-group button.active {
  background-color: #6d4c41;
}

/* Контейнер для таблиц */
.component-container {
  width: 90%; /* Почти во всю ширину экрана */
  height: 70vh; /* Почти во всю высоту экрана */
  border: 2px solid #4e342e;
  border-radius: 10px;
  padding: 20px;
  background: #ffffff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  overflow-y: auto; /* Прокрутка, если таблица выходит за пределы контейнера */
}

/* Таблицы */
.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Arial', sans-serif;
  font-size: 14px;
}

.styled-table thead tr {
  background-color: #4e342e; /* Тёмно-коричневый цвет */
  color: #fff; /* Белый текст */
  text-align: left;
}

.styled-table th,
.styled-table td {
  padding: 12px 15px;
  border: 1px solid #ddd;
}

.styled-table tbody tr {
  background-color: #f5e9e2; /* Светлый кофейный тон */
}

.styled-table tbody tr:nth-child(even) {
  background-color: #e9d6cc; /* Немного темнее для чётных строк */
}

.styled-table tbody tr:hover {
  background-color: #d6c3b4; /* Подсветка строки при наведении */
  cursor: pointer;
}
</style>