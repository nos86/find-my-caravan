<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-100">
        <h2 class="font-bold text-lg text-gray-900">🔄 Confronto annunci ({{ listings.length }})</h2>
        <button class="btn-ghost" @click="emit('close')">✕ Chiudi</button>
      </div>

      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-200 border-t-indigo-600" />
      </div>

      <div v-else class="overflow-auto flex-1">
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="bg-gray-50">
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide w-40 sticky left-0 bg-gray-50 border-r border-gray-100">
                Campo
              </th>
              <th
                v-for="l in listings"
                :key="l.id"
                class="px-4 py-3 text-center min-w-[200px] border-b border-gray-100"
              >
                <div class="flex flex-col items-center gap-1">
                  <span class="font-semibold text-gray-800 text-xs line-clamp-2">{{ l.title }}</span>
                  <span class="text-xl font-bold text-indigo-700">{{ formatPrice(l.price) }}</span>
                  <button
                    class="text-xs text-red-500 hover:text-red-700 underline"
                    @click="emit('remove', l.id)"
                  >
                    Rimuovi
                  </button>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in compareRows"
              :key="row.field"
              class="border-b border-gray-50 hover:bg-gray-50 transition-colors"
            >
              <td class="px-4 py-2 text-xs font-medium text-gray-500 sticky left-0 bg-white border-r border-gray-100">
                {{ row.label }}
              </td>
              <td
                v-for="l in listings"
                :key="l.id"
                class="px-4 py-2 text-center text-sm"
                :class="highlightClass(row, l)"
              >
                {{ row.format(l) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Listing } from '../types/listing'
import { fetchListing } from '../api/listings'

const props = defineProps<{ ids: number[] }>()
const emit = defineEmits<{ close: []; remove: [id: number] }>()

const listings = ref<Listing[]>([])
const loading = ref(true)

onMounted(async () => {
  loading.value = true
  listings.value = await Promise.all(props.ids.map(fetchListing))
  loading.value = false
})

interface CompareRow {
  field: keyof Listing
  label: string
  format: (l: Listing) => string
  best?: 'min' | 'max'
}

const compareRows: CompareRow[] = [
  { field: 'year', label: 'Anno', format: (l) => l.year?.toString() ?? '—', best: 'max' },
  { field: 'price', label: 'Prezzo', format: (l) => formatPrice(l.price), best: 'min' },
  { field: 'mileage_km', label: 'Km', format: (l) => l.mileage_km ? new Intl.NumberFormat('it-IT').format(l.mileage_km) + ' km' : '—', best: 'min' },
  { field: 'brand', label: 'Marca', format: (l) => l.brand ?? '—' },
  { field: 'model', label: 'Modello', format: (l) => l.model ?? '—' },
  { field: 'layout_type', label: 'Tipo carrozzeria', format: (l) => l.layout_type ?? '—' },
  { field: 'length_mm', label: 'Lunghezza', format: (l) => l.length_mm ? (l.length_mm / 1000).toFixed(2) + ' m' : '—' },
  { field: 'mass_kg', label: 'Massa', format: (l) => l.mass_kg ? l.mass_kg + ' kg' : '—', best: 'min' },
  { field: 'seats_travel', label: 'Posti viaggio', format: (l) => l.seats_travel?.toString() ?? '—', best: 'max' },
  { field: 'seats_sleeping', label: 'Posti letto', format: (l) => l.seats_sleeping?.toString() ?? '—', best: 'max' },
  { field: 'has_rear_garage', label: 'Garage', format: (l) => boolLabel(l.has_rear_garage) },
  { field: 'has_bunk_beds', label: 'Letti castello', format: (l) => boolLabel(l.has_bunk_beds) },
  { field: 'has_double_floor', label: 'Doppio pavimento', format: (l) => boolLabel(l.has_double_floor) },
  { field: 'air_conditioning', label: 'Aria condizionata', format: (l) => boolLabel(l.air_conditioning) },
  { field: 'solar_panel', label: 'Pannello solare', format: (l) => boolLabel(l.solar_panel) },
  { field: 'fuel_type', label: 'Carburante', format: (l) => l.fuel_type ?? '—' },
  { field: 'engine_power_kw', label: 'Potenza', format: (l) => l.engine_power_kw ? l.engine_power_kw + ' kW' : '—', best: 'max' },
  { field: 'emission_class', label: 'Euro', format: (l) => l.emission_class ?? '—' },
  { field: 'driving_license_category', label: 'Patente', format: (l) => l.driving_license_category ?? '—' },
  { field: 'seller_type', label: 'Venditore', format: (l) => l.seller_type === 'dealer' ? 'Concessionario' : l.seller_type === 'private' ? 'Privato' : '—' },
  { field: 'region', label: 'Regione', format: (l) => l.region ?? '—' },
  { field: 'city', label: 'Città', format: (l) => l.city ?? '—' },
  { field: 'extraction_confidence', label: 'Qualità dati', format: (l) => l.extraction_confidence ? Math.round(l.extraction_confidence * 100) + '%' : '—', best: 'max' },
]

function highlightClass(row: CompareRow, listing: Listing): string {
  if (!row.best || listings.value.length < 2) return ''
  const vals = listings.value
    .map((l) => l[row.field] as number | null)
    .filter((v): v is number => v !== null)
  if (!vals.length) return ''
  const val = listing[row.field] as number | null
  if (val === null) return ''
  const best = row.best === 'min' ? Math.min(...vals) : Math.max(...vals)
  return val === best ? 'bg-green-50 text-green-800 font-semibold' : ''
}

function formatPrice(price: number | null): string {
  if (price === null) return '—'
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(price)
}

function boolLabel(val: boolean | null): string {
  if (val === null || val === undefined) return '—'
  return val ? '✅ Sì' : '❌ No'
}
</script>
