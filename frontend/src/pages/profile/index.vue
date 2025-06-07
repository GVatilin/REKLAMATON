<script setup>
import { authUser } from "../schedule/components/ScheduleFunctions";
import invalidUserPanelAuth from './components/NotAuthorized.vue';
import navPanel from "./components/NavPad.vue";
import userAvatar from "./components/UserAvatar.vue";
import SettingsButton from "./components/SettingsButton.vue";
import TodayTasks from "./components/TodayTasks.vue";
import StatisticData from "./components/StatisticData.vue";
//import UserSettings from "./components/UserSettings.vue";
import { onMounted, ref } from "vue";


const user = ref("")

async function authUserWrap() {
    user.value = await authUser()
}

onMounted(async () => {
    await authUserWrap()
})
</script>

<template>
  <div class="profile-page">
    <navPanel />
    <div>
      <userAvatar />
    </div>
    <div>
      <SettingsButton />
    </div>
    <div>
      <TodayTasks />
    </div>
    <div>
      <StatisticData />
    </div>
    <div>
      <UserSettings />
    </div>
    <invalidUserPanelAuth v-show="user == -1"/>
  </div>
</template>

<style scoped>
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
}

.profile-page {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #1e1e2e;
  color: #cdd6f4;
  font-family: "Roboto", sans-serif;
  padding: 20px;
  overflow: auto; /* позволит скроллить содержимое */
}

</style>
