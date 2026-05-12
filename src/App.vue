<template>
  <div id="app">
    <TrafficDashboard />
  </div>
</template>

<script>
import TrafficDashboard from './components/TrafficDashboard.vue'

export default {
  name: 'App',
  components: {
    TrafficDashboard
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background: transparent;
}
</style>
