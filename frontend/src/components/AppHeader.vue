<template>
  <header class="bg-white border-b border-gray-200 sticky top-0 z-40">
    <div class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center gap-2 font-bold text-lg text-indigo-700 hover:text-indigo-800 transition-colors">
          <span class="text-2xl">🚌</span>
          <span class="hidden sm:inline">Find My Caravan</span>
        </RouterLink>

        <!-- Nav -->
        <nav class="flex items-center gap-1">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-gray-600 hover:text-indigo-700 hover:bg-indigo-50 transition-all"
            active-class="text-indigo-700 bg-indigo-50"
          >
            <span>{{ link.icon }}</span>
            <span class="hidden sm:inline">{{ link.label }}</span>
          </RouterLink>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

const navLinks = [
  { to: '/', label: 'Dashboard', icon: '🔍' },
  { to: '/import', label: 'Importa', icon: '📥' },
  { to: '/sources', label: 'Sorgenti', icon: '📡' },
  { to: '/models', label: 'Modelli', icon: '🚐' },
]
</script>
