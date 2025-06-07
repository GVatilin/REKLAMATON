<script setup>
import { onMounted, ref, watch } from "vue"
import { registerUser, loginUser } from "./LoginFunctions.js"
import { useRouter, useRoute } from "vue-router"
import loading from "./Loading.vue";

const router = useRouter()
const route = useRoute()

const registration = ref(-1)

const username = ref("")
const email = ref("")
const password = ref("")
const response = ref("")
const isLoading = ref(false)

async function registerUserWrap() {
    isLoading.value = true
    response.value = await registerUser(email.value, username.value, password.value)
    if (response.value === "") {
        await loginUserWrap()
    }
    isLoading.value = false
}

async function loginUserWrap() {
    isLoading.value = true
    response.value = await loginUser(email.value, password.value)
    if (response.value === "") {
        router.push({
            name: "Profile Page"
        })
    }
    isLoading.value = false
}

async function googleLogin() {
    const authUrl = `http://${process.env.VUE_APP_DNS_URL}/api/v1/auth/google/login`
    window.location.href = authUrl;
}

function clearFields() {
    username.value = ""
    email.value = ""
    password.value = ""
    response.value = ""
}

watch(registration, clearFields)

onMounted(() => {
    if (route.meta.isLogin) {
        registration.value = 0
    } else {
        registration.value = 1
    }
})
</script>

<template>
    <div>
        <loading v-show="isLoading"/>
        <div class="login-main">
            <div class="container">
                <div class="welcome-text">
                    <h1>Добро пожаловать в <span class="chrono">Chrono!</span></h1>
                    <h2>Каждый миг на счету - планируй с умом, <br> а мы поможем!</h2>
                    <p class="error-msg" style="text-align: left;">{{ response }}</p>
                </div>

                <transition :class="{ hidden: registration == -1 }" name="slide" mode="out-in">
                    <div class="input-container" :key="registration">
                        <div class="input-wrapper" :class="{ hidden: registration == 0 }">
                            <input placeholder="Username" v-model="username"/>
                        </div>
                        <div class="input-wrapper">
                            <input placeholder="Email" v-model="email"/>
                        </div>
                        <div class="input-wrapper">
                            <input placeholder="Password" v-model="password" type="password" />
                        </div>

                        <button v-if="registration" @click="registerUserWrap">Зарегистрироваться</button>
                        <button v-else @click="loginUserWrap">Войти</button>

                        <div
                            v-if="registration"
                            class="bottom-text"
                            @click="registration = !registration"
                        >
                            Уже есть аккаунт (войти)
                        </div>
                        <div
                            v-else
                            class="bottom-text"
                            @click="registration = (registration + 1) % 2"
                        >
                            Еще нет аккаунта (зарегистрироваться)
                        </div>
                        <div
                            class="bottom-text"
                            style="margin-top: 2%;"
                            @click="googleLogin"
                        >
                            Войти через <b>Google</b>
                        </div>
                    </div>
                </transition>
            </div>
        </div>
    </div>
</template>

<style scoped>
@import "./LoginContainer.css";
</style>