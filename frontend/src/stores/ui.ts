import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarOpen = ref(true)
  const activeDetailId = ref<number | null>(null)
  const showComparison = ref(false)
  const activeTab = ref<'lista' | 'mappa' | 'grafico'>('lista')

  function openDetail(id: number) {
    activeDetailId.value = id
  }

  function closeDetail() {
    activeDetailId.value = null
  }

  function openComparison() {
    showComparison.value = true
  }

  function closeComparison() {
    showComparison.value = false
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  return {
    sidebarOpen,
    activeDetailId,
    showComparison,
    activeTab,
    openDetail,
    closeDetail,
    openComparison,
    closeComparison,
    toggleSidebar,
  }
})
