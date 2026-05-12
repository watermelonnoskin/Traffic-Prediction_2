<template>
  <div id="app">
    <LoginPage v-if="!isLoggedIn" @login-success="handleLoginSuccess" />
    <TrafficDashboard v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginPage from './components/LoginPage.vue'
import TrafficDashboard from './components/TrafficDashboard.vue'

const isLoggedIn = ref(false)

const handleLoginSuccess = () => {
  isLoggedIn.value = true
}
</script>

<style>
#app {
  min-height: 100vh;
  background: transparent;
}
</style>
