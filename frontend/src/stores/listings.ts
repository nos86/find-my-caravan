import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ListingFilters, ListingSearchResult } from '../types/listing'
import { fetchListings } from '../api/listings'

export const useListingsStore = defineStore('listings', () => {
  const filters = ref<ListingFilters>({ page: 1, page_size: 24, only_active: true })
  const results = ref<ListingSearchResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedForComparison = ref<number[]>([])

  function setFilters(newFilters: ListingFilters) {
    filters.value = { ...newFilters, page: 1 }
  }

  function patchFilters(patch: Partial<ListingFilters>) {
    filters.value = { ...filters.value, ...patch }
  }

  async function search() {
    loading.value = true
    error.value = null
    try {
      results.value = await fetchListings(filters.value)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Errore durante la ricerca'
    } finally {
      loading.value = false
    }
  }

  function toggleComparison(id: number) {
    const idx = selectedForComparison.value.indexOf(id)
    if (idx === -1) {
      if (selectedForComparison.value.length < 4) {
        selectedForComparison.value.push(id)
      }
    } else {
      selectedForComparison.value.splice(idx, 1)
    }
  }

  function clearComparison() {
    selectedForComparison.value = []
  }

  return {
    filters,
    results,
    loading,
    error,
    selectedForComparison,
    setFilters,
    patchFilters,
    search,
    toggleComparison,
    clearComparison,
  }
})
