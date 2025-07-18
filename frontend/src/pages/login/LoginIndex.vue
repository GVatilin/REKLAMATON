<script setup>
import mainContainer from "./components/LoginPage.vue"
import canvasPanel from "../../components/CanvasPanel.vue"
document.title = "Login"
</script>

<template>
    <div class="grey-style">
        <mainContainer />
        <canvasPanel />
    </div>
</template>

<style scoped>
@import "./components/LoginContainer.css";
</style>