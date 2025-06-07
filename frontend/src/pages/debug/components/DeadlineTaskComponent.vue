<template>
    <div>
      <h1>Список дедлайнов</h1>
      <table class="styled-table">
        <!-- Заголовки таблицы -->
        <thead>
          <tr>
            <th>ID</th>
            <th>Author</th>
            <th>Author ID</th>
            <th>Deadline Time</th>
            <th>Description</th>
            <th>Status</th>
            <th>Priority</th>
          </tr>
        </thead>
        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="task in deadline_tasks" :key="task.id">
            <td>{{ task.id }}</td>
            <td>{{ task.author }}</td>
            <td>{{ task.author_id }}</td>
            <td>{{ task.deadline_time }}</td>
            <td>{{ task.description }}</td>
            <td>{{ task.status }}</td>
            <td>{{ task.priority }}</td>
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
        deadline_tasks: []
    }
},
methods: {
    async get_tasks() {
        const response = await axios.get('http://localhost:8080/api/v1/deadline_task/debug/deadline_tasks_table/');
        this.deadline_tasks = response.data;
    }
},
mounted() {
    // Загружаем пользователей при монтировании компонента
    this.get_tasks();
  },

name: 'DeadlineTaskDebugComponent'  
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