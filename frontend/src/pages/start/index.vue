<script setup>

import navPanel from "./components/NavPanel.vue"
import StartButton from "./components/StartButton.vue"
import ChronoStart from "./components/ChronoStart.vue";
</script>
<template>
  <div class="start-page">
    <navPanel />
    <div class="content">
      <StartButton />
    </div>
    <div>
        <ChronoStart />
    </div>

  </div>

</template>
<style>
.start-page {
  font-family: "Roboto", sans-serif;    
  background-image: url('./../../assets/main 3.PNG');
}
@media (max-width: 768px) {
  .start-page {
    background-size: cover;
    background-position: center;
  }
}
</style>