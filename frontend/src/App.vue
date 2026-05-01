<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />
    <div class="flex-1 flex flex-col">
      <RouterView />
    </div>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import { RouterView } from 'vue-router'
</script>
