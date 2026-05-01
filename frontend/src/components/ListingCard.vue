<template>
  <div
    class="card group cursor-pointer hover:shadow-md transition-shadow duration-200 flex flex-col"
    @click="emit('open-detail', listing.id)"
  >
    <!-- Image -->
    <div class="relative aspect-video bg-gray-100 overflow-hidden flex-shrink-0">
      <img
        v-if="firstImage"
        :src="firstImage"
        :alt="listing.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        loading="lazy"
        @error="imageError = true"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-300 text-5xl">
        🚌
      </div>

      <!-- Confidence dot -->
      <div class="absolute top-2 right-2">
        <ConfidenceBadge :confidence="listing.extraction_confidence" />
      </div>

      <!-- Source badge -->
      <div v-if="listing.source_name" class="absolute bottom-2 left-2">
        <span class="badge-gray text-xs px-1.5 py-0.5 rounded bg-black/50 text-white text-[10px]">
          {{ listing.source_name }}
        </span>
      </div>

      <!-- Compare checkbox -->
      <div class="absolute top-2 left-2" @click.stop>
        <input
          type="checkbox"
          :checked="isSelected"
          class="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
          :title="isSelected ? 'Rimuovi dal confronto' : 'Aggiungi al confronto'"
          @change="emit('toggle-compare', listing.id)"
        />
      </div>
    </div>

    <!-- Body -->
    <div class="p-3 flex flex-col gap-1.5 flex-1">
      <!-- Title -->
      <h3 class="font-semibold text-sm text-gray-900 line-clamp-2 leading-snug">
        {{ listing.title }}
      </h3>

      <!-- Price -->
      <div class="text-xl font-bold text-indigo-700">
        {{ formatPrice(listing.price) }}
      </div>

      <!-- Meta row -->
      <div class="flex items-center gap-2 text-xs text-gray-500 flex-wrap">
        <span v-if="listing.year">📅 {{ listing.year }}</span>
        <span v-if="listing.mileage_km">🛣️ {{ formatKm(listing.mileage_km) }}</span>
        <span v-if="listing.brand">{{ listing.brand }}<span v-if="listing.model"> {{ listing.model }}</span></span>
      </div>

      <!-- Location -->
      <div class="text-xs text-gray-400 truncate">
        📍 {{ locationText }}
      </div>

      <!-- Seller -->
      <div class="flex items-center gap-1.5 flex-wrap">
        <span v-if="listing.seller_name" class="text-xs text-gray-600 truncate max-w-[120px]">
          {{ listing.seller_name }}
        </span>
        <span v-if="listing.seller_type" :class="sellerBadgeClass">
          {{ sellerTypeLabel }}
        </span>
      </div>

      <!-- Feature pills -->
      <div class="flex flex-wrap gap-1 mt-auto pt-1">
        <span v-if="listing.layout_type" class="pill">{{ listing.layout_type }}</span>
        <span v-if="listing.has_rear_garage" class="pill">garage</span>
        <span v-if="listing.seats_sleeping" class="pill">{{ listing.seats_sleeping }} letti</span>
        <span v-if="listing.air_conditioning" class="pill">clima</span>
        <span v-if="listing.solar_panel" class="pill">solare</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="px-3 pb-3 flex gap-1.5" @click.stop>
      <button
        v-if="listing.source_url"
        class="btn-secondary text-xs flex-1"
        @click="openExternal"
      >
        🔗 Originale
      </button>
      <button class="btn-primary text-xs flex-1" @click="emit('open-detail', listing.id)">
        Dettaglio
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Listing } from '../types/listing'
import ConfidenceBadge from './ConfidenceBadge.vue'

const props = defineProps<{
  listing: Listing
  isSelected: boolean
}>()

const emit = defineEmits<{
  'open-detail': [id: number]
  'toggle-compare': [id: number]
}>()

const imageError = ref(false)

const firstImage = computed(() => {
  if (imageError.value || !props.listing.images?.length) return null
  return props.listing.images[0]
})

const locationText = computed(() => {
  const parts = [props.listing.city, props.listing.province, props.listing.region].filter(Boolean)
  return parts.length ? parts.join(', ') : 'Posizione non disponibile'
})

const sellerTypeLabel = computed(() => {
  if (props.listing.seller_type === 'dealer') return 'Concessionario'
  if (props.listing.seller_type === 'private') return 'Privato'
  return props.listing.seller_type ?? ''
})

const sellerBadgeClass = computed(() => {
  if (props.listing.seller_type === 'dealer') return 'badge-blue'
  if (props.listing.seller_type === 'private') return 'badge-green'
  return 'badge-gray'
})

function formatPrice(price: number | null): string {
  if (price === null) return 'Prezzo N/D'
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(price)
}

function formatKm(km: number | null): string {
  if (km === null) return 'N/D'
  return new Intl.NumberFormat('it-IT').format(km) + ' km'
}

function openExternal() {
  if (props.listing.source_url) window.open(props.listing.source_url, '_blank', 'noopener')
}
</script>
