<template>
  <div class="w-full h-[500px] rounded-xl overflow-hidden border border-gray-200" ref="mapContainer" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { MapListing } from '../api/listings'

const props = defineProps<{
  listings: MapListing[]
}>()

const emit = defineEmits<{ 'open-detail': [id: number] }>()

const mapContainer = ref<HTMLElement | null>(null)
let map: import('leaflet').Map | null = null
let markers: import('leaflet').Marker[] = []

type LeafletLib = typeof import('leaflet')

async function initMap() {
  if (!mapContainer.value) return
  const L: LeafletLib = await import('leaflet')

  // Fix default icon paths for Vite
  delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  map = L.map(mapContainer.value).setView([44.5, 11], 6)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map)

  renderMarkers(L)
}

function renderMarkers(L: LeafletLib) {
  if (!map) return

  markers.forEach((m) => m.remove())
  markers = []

  props.listings.forEach((listing) => {
    if (!listing.latitude || !listing.longitude) return

    const price = listing.price
      ? new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(listing.price)
      : 'N/D'

    const popup = `
      <div style="min-width:160px">
        <strong style="font-size:12px">${listing.title}</strong><br/>
        <span style="color:#4f46e5;font-weight:bold">${price}</span>
        ${listing.year ? ` · ${listing.year}` : ''}<br/>
        ${listing.seller_type === 'dealer' ? '<span style="font-size:11px">Concessionario</span>' : '<span style="font-size:11px">Privato</span>'}<br/>
        <button
          onclick="window.__openListing(${listing.id})"
          style="margin-top:6px;padding:3px 8px;background:#4f46e5;color:white;border:none;border-radius:4px;font-size:11px;cursor:pointer"
        >Vedi dettaglio</button>
      </div>
    `

    const marker = L.marker([listing.latitude, listing.longitude])
      .addTo(map!)
      .bindPopup(popup)

    markers.push(marker)
  })
}

// Global handler for popup button clicks
;(window as unknown as Record<string, unknown>).__openListing = (id: number) => {
  emit('open-detail', id)
}

onMounted(initMap)

watch(() => props.listings, async () => {
  const L: LeafletLib = await import('leaflet')
  renderMarkers(L)
})

onUnmounted(() => {
  map?.remove()
  map = null
})
</script>
