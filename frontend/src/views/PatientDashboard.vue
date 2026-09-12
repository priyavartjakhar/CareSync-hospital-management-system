<template>
  <div class="dash-frame">
    <iframe title="CareSync Patient Dashboard" :src="dashboardUrl"></iframe>
  </div>
</template>

<script setup>
const dashboardUrl = `${import.meta.env.BASE_URL}designs/PatientDashboard-full.html`
</script>

<style scoped>
.dash-frame {
  height: calc(100vh - 0px);
}
iframe {
  width: 100%;
  height: 100vh;
  border: 0;
  display: block;
}
</style>
