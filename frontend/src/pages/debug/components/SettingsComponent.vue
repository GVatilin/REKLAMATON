<template>
    <div>
      <h1>Список задач в календаре</h1>
      <table class="styled-table">
        <!-- Заголовки таблицы -->
        <thead>
          <tr>
            <th>ID</th>
            <th>User ID</th>
            <th>Text Settings</th>
            <th>Start Working</th>
            <th>End Working</th>
          </tr>
        </thead>
        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="setting in settings" :key="setting.id">
            <td>{{ setting.id }}</td>
            <td>{{ setting.user_id }}</td>
            <td>{{ setting.text_settings }}</td>
            <td>{{ setting.start_working }}</td>
            <td>{{ setting.end_working }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
<script>
import axios from 'axios';
export default {
data() {
    return {
        settings: []
    }
},
methods: {
    async get_settings() {
        const response = await axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/get_settings_debug`);
        this.settings = response.data;
    }
},
mounted() {
    // Загружаем пользователей при монтировании компонента
    this.get_settings();
  },

name: 'SettingsComponent'  
};

</script>

<style>
.styled-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Arial', sans-serif;
  font-size: 14px;
  margin-top: 20px;
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

.styled-table tbody td {
  color: #4e342e; /* Тёмно-коричневый текст */
}

.styled-table thead th {
  font-weight: bold;
  text-transform: uppercase;
}
</style>