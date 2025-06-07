<template>
    <div>
      <h1>Список пользователей</h1>
      <table class="styled-table">
        <!-- Заголовки таблицы -->
        <thead>
          <tr>
            <th>ID</th>
            <th>Email</th>
            <th>Username</th>
            <th>Premium</th>
            <th>Password</th>
          </tr>
        </thead>
        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.premium ? 'Yes' : 'No' }}</td>
            <td>{{ user.password }}</td>
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
        users: []
    }
},
methods: {
    async get_users() {
        const response = await axios.get('http://localhost:8080/api/v1/user/debug/users_table/');
        this.users = response.data;
    }
},
mounted() {
    // Загружаем пользователей при монтировании компонента
    this.get_users();
  },

name: 'UserDebugComponent'  
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