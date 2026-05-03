<template>
  <div class="max-w-screen-xl mx-auto px-4 py-6">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">🚐 Modelli e marche</h1>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-200 border-t-indigo-600" />
    </div>

    <div v-else-if="error" class="p-4 bg-red-50 rounded-lg text-red-700">{{ error }}</div>

    <div v-else class="space-y-6">
      <!-- Price by brand chart -->
      <div class="card p-5">
        <h2 class="text-base font-semibold text-gray-800 mb-4">Prezzo medio per marca</h2>
        <div class="space-y-2">
          <div
            v-for="item in priceByBrand.slice(0, 20)"
            :key="item.brand"
            class="flex items-center gap-3"
          >
            <div class="w-28 text-sm text-gray-700 truncate font-medium">{{ item.brand }}</div>
            <div class="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden relative">
              <div
                class="h-full bg-indigo-500 rounded-full flex items-center justify-end pr-2 transition-all duration-500"
                :style="{ width: `${(item.avg_price / maxBrandPrice) * 100}%` }"
              >
                <span class="text-white text-xs font-medium">{{ formatPrice(item.avg_price) }}</span>
              </div>
            </div>
            <span class="text-xs text-gray-400 w-16 text-right">{{ item.count }} annunci</span>
          </div>
        </div>
      </div>

      <!-- Price distribution -->
      <div class="card p-5">
        <h2 class="text-base font-semibold text-gray-800 mb-4">Distribuzione prezzi</h2>
        <div class="flex items-end gap-1 h-32">
          <div
            v-for="bin in priceDistribution"
            :key="bin.bin"
            class="flex-1 bg-indigo-400 hover:bg-indigo-500 rounded-t transition-colors cursor-default relative group"
            :style="{ height: `${(bin.count / maxDistCount) * 100}%`, minHeight: bin.count ? '4px' : '0' }"
          >
            <div class="absolute -top-6 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs rounded px-1 py-0.5 opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none z-10">
              {{ bin.bin }}: {{ bin.count }}
            </div>
          </div>
        </div>
        <div class="flex justify-between text-xs text-gray-400 mt-1">
          <span v-if="priceDistribution.length">{{ priceDistribution[0]?.bin }}</span>
          <span v-if="priceDistribution.length">{{ priceDistribution[priceDistribution.length - 1]?.bin }}</span>
        </div>
      </div>

      <!-- Price by region -->
      <div class="card p-5">
        <h2 class="text-base font-semibold text-gray-800 mb-4">Prezzo medio per regione</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="item in priceByRegion"
            :key="item.region"
            class="bg-gray-50 rounded-lg p-3"
          >
            <div class="font-medium text-sm text-gray-800">{{ item.region }}</div>
            <div class="text-lg font-bold text-indigo-700">{{ formatPrice(item.avg_price) }}</div>
            <div class="text-xs text-gray-400">{{ item.count }} annunci</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fetchPriceByBrand, fetchPriceDistribution, fetchPriceByRegion } from '../api/analytics'
import type { PriceByBrand, PriceDistributionBin, PriceByRegion } from '../types/analytics'

const priceByBrand = ref<PriceByBrand[]>([])
const priceDistribution = ref<PriceDistributionBin[]>([])
const priceByRegion = ref<PriceByRegion[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const maxBrandPrice = computed(() => Math.max(...priceByBrand.value.map((b) => b.avg_price), 1))
const maxDistCount = computed(() => Math.max(...priceDistribution.value.map((b) => b.count), 1))

function formatPrice(price: number): string {
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(price)
}

onMounted(async () => {
  loading.value = true
  error.value = null
  try {
    ;[priceByBrand.value, priceDistribution.value, priceByRegion.value] = await Promise.all([
      fetchPriceByBrand(),
      fetchPriceDistribution(),
      fetchPriceByRegion(),
    ])
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Errore caricamento dati'
  } finally {
    loading.value = false
  }
})
</script>
