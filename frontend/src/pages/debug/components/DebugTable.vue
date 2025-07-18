<template>
    <div>
      <h1>{{ title }}</h1>
      <table class="styled-table">
        <!-- Заголовки таблицы -->
        <thead>
          <tr>
            <th v-for="col in columns" :key="col">{{ col }}</th>
          </tr>
        </thead>
        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="row in rows" :key="row.id || JSON.stringify(row)">
            <td v-for="col in columns" :key="col">{{ row[col] }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
<script>
import axios from 'axios';

export default {
  name: 'DebugTable',
  props: {
    endpoint: { type: String, required: true },
    title: { type: String, default: '' }
  },
  data() {
    return {
      rows: [],
      error: null
    };
  },
  computed: {
    columns() {
      return this.rows.length ? Object.keys(this.rows[0]) : [];
    }
  },
  methods: {
    async fetchData() {
      this.error = null;
      try {
        const response = await axios.get(this.endpoint);
        this.rows = Array.isArray(response.data) ? response.data : [];
      } catch (err) {
        this.error = err.response?.statusText || err.message;
      }
    }
  },
  watch: {
    endpoint: 'fetchData'
  },
  mounted() {
    this.fetchData();
  }
};
</script>


<style scoped>
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