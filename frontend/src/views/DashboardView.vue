<template>
  <div class="flex-1 flex overflow-hidden">
    <!-- Sidebar backdrop (mobile) -->
    <div
      v-if="uiStore.sidebarOpen && isMobile"
      class="fixed inset-0 bg-black/40 z-20 lg:hidden"
      @click="uiStore.toggleSidebar()"
    />

    <!-- Sidebar -->
    <aside
      class="fixed lg:relative top-14 lg:top-0 left-0 h-[calc(100vh-3.5rem)] lg:h-auto w-72 bg-white border-r border-gray-200 overflow-y-auto z-30 transition-transform duration-300 flex-shrink-0 p-4"
      :class="uiStore.sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <SearchFilters v-model="listingsStore.filters" @search="onSearch" />
    </aside>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto">
      <!-- Toolbar -->
      <div class="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 z-10 px-4 py-2">
        <div class="max-w-screen-xl mx-auto flex items-center gap-3 flex-wrap">
          <!-- Sidebar toggle -->
          <button class="btn-ghost text-sm" @click="uiStore.toggleSidebar()">
            <span>☰</span>
            <span class="hidden sm:inline">Filtri</span>
          </button>

          <!-- Result count -->
          <span class="text-sm text-gray-500">
            <span v-if="listingsStore.loading">Caricamento...</span>
            <span v-else>{{ listingsStore.results?.total ?? 0 }} annunci trovati</span>
          </span>

          <!-- Tabs -->
          <div class="flex gap-1 bg-gray-100 rounded-lg p-1 ml-auto">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="px-3 py-1 rounded-md text-sm font-medium transition-all"
              :class="uiStore.activeTab === tab.key ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
              @click="uiStore.activeTab = tab.key as typeof uiStore.activeTab"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Compare button -->
          <button
            v-if="listingsStore.selectedForComparison.length >= 2"
            class="btn-primary text-sm"
            @click="uiStore.openComparison()"
          >
            🔄 Confronta ({{ listingsStore.selectedForComparison.length }})
          </button>
        </div>
      </div>

      <div class="max-w-screen-xl mx-auto px-4 py-4">
        <!-- Error -->
        <div v-if="listingsStore.error" class="mb-4 p-3 bg-red-50 rounded-lg border border-red-200 text-red-700 text-sm">
          ⚠️ {{ listingsStore.error }}
        </div>

        <!-- LISTA tab -->
        <div v-if="uiStore.activeTab === 'lista'">
          <!-- Loading skeleton -->
          <div v-if="listingsStore.loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="i in 9" :key="i" class="card animate-pulse">
              <div class="aspect-video bg-gray-200" />
              <div class="p-3 space-y-2">
                <div class="h-4 bg-gray-200 rounded w-3/4" />
                <div class="h-6 bg-gray-200 rounded w-1/2" />
                <div class="h-3 bg-gray-200 rounded w-full" />
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div
            v-else-if="!listingsStore.results?.items?.length"
            class="flex flex-col items-center justify-center py-20 gap-3 text-gray-400"
          >
            <span class="text-6xl">🔍</span>
            <p class="text-lg font-medium">Nessun annuncio trovato</p>
            <p class="text-sm">Prova a modificare i filtri di ricerca</p>
          </div>

          <!-- Grid -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <ListingCard
              v-for="listing in listingsStore.results.items"
              :key="listing.id"
              :listing="listing"
              :is-selected="listingsStore.selectedForComparison.includes(listing.id)"
              @open-detail="openDetail"
              @toggle-compare="listingsStore.toggleComparison($event)"
            />
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-8">
            <button
              class="btn-secondary text-sm"
              :disabled="currentPage <= 1"
              @click="goToPage(currentPage - 1)"
            >
              ← Precedente
            </button>
            <div class="flex gap-1">
              <button
                v-for="p in visiblePages"
                :key="p"
                class="w-8 h-8 rounded-lg text-sm font-medium transition-all"
                :class="p === currentPage ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'"
                @click="goToPage(p)"
              >
                {{ p }}
              </button>
            </div>
            <button
              class="btn-secondary text-sm"
              :disabled="currentPage >= totalPages"
              @click="goToPage(currentPage + 1)"
            >
              Successiva →
            </button>
          </div>
        </div>

        <!-- MAPPA tab -->
        <div v-else-if="uiStore.activeTab === 'mappa'">
          <ListingMap
            :listings="mapListings"
            @open-detail="openDetail"
          />
          <p class="text-xs text-gray-400 mt-2 text-center">
            {{ mapListings.length }} annunci con coordinate geografiche
          </p>
        </div>

        <!-- GRAFICO tab -->
        <div v-else-if="uiStore.activeTab === 'grafico'">
          <div class="card p-4">
            <PriceYearChart :filters="chartFilters" @open-detail="openDetail" />
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- Detail modal -->
  <ListingDetail
    v-model="showDetail"
    :listing-id="uiStore.activeDetailId"
    @sold="onSold"
  />

  <!-- Comparison modal -->
  <div v-if="uiStore.showComparison" class="fixed inset-0 z-50">
    <ComparisonView
      :ids="listingsStore.selectedForComparison"
      @close="uiStore.closeComparison()"
      @remove="listingsStore.toggleComparison($event)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useWindowSize } from '@vueuse/core'
import { useListingsStore } from '../stores/listings'
import { useUiStore } from '../stores/ui'
import { fetchMapListings } from '../api/listings'
import type { MapListing } from '../api/listings'
import SearchFilters from '../components/SearchFilters.vue'
import ListingCard from '../components/ListingCard.vue'
import ListingDetail from '../components/ListingDetail.vue'
import ListingMap from '../components/ListingMap.vue'
import PriceYearChart from '../components/PriceYearChart.vue'
import ComparisonView from '../components/ComparisonView.vue'

const listingsStore = useListingsStore()
const uiStore = useUiStore()

const { width } = useWindowSize()
const isMobile = computed(() => width.value < 1024)

const showDetail = computed({
  get: () => uiStore.activeDetailId !== null,
  set: (val) => { if (!val) uiStore.closeDetail() },
})

const tabs = [
  { key: 'lista', label: '📋 Lista' },
  { key: 'mappa', label: '🗺️ Mappa' },
  { key: 'grafico', label: '📊 Grafico' },
]

const currentPage = computed(() => listingsStore.filters.page ?? 1)
const totalPages = computed(() => listingsStore.results?.pages ?? 1)

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(5, total)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

const mapListings = ref<MapListing[]>([])
const chartFilters = computed(() => ({ ...listingsStore.filters }))

async function loadMapListings() {
  try {
    mapListings.value = await fetchMapListings(listingsStore.filters)
  } catch { /* ignore */ }
}

function onSearch() {
  listingsStore.search()
  if (uiStore.activeTab === 'mappa') loadMapListings()
}

function goToPage(page: number) {
  listingsStore.patchFilters({ page })
  listingsStore.search()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openDetail(id: number) {
  uiStore.openDetail(id)
}

function onSold(_id: number) {
  listingsStore.search()
}

watch(() => uiStore.activeTab, (tab) => {
  if (tab === 'mappa') loadMapListings()
})

onMounted(() => {
  listingsStore.search()
})
</script>
