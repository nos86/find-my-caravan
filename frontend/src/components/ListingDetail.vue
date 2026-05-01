<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-stretch sm:items-center justify-center p-0 sm:p-4"
        @click.self="emit('update:modelValue', false)"
      >
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="emit('update:modelValue', false)" />

        <!-- Panel -->
        <div class="relative bg-white w-full sm:max-w-4xl sm:rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-screen sm:max-h-[90vh] z-10">
          <!-- Loading state -->
          <div v-if="loading" class="flex items-center justify-center py-24">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600" />
          </div>

          <!-- Error state -->
          <div v-else-if="error" class="flex flex-col items-center justify-center py-24 gap-3">
            <span class="text-4xl">⚠️</span>
            <p class="text-red-600 font-medium">{{ error }}</p>
            <button class="btn-secondary" @click="load">Riprova</button>
          </div>

          <template v-else-if="listing">
            <!-- Header -->
            <div class="flex items-start justify-between p-4 border-b border-gray-100 flex-shrink-0">
              <div class="flex-1 min-w-0 pr-4">
                <h2 class="font-bold text-lg text-gray-900 leading-tight">{{ listing.title }}</h2>
                <div class="flex items-center gap-3 mt-1 flex-wrap">
                  <span class="text-2xl font-bold text-indigo-700">{{ formatPrice(listing.price) }}</span>
                  <span v-if="listing.year" class="text-gray-500 text-sm">{{ listing.year }}</span>
                  <span class="badge-gray text-xs">{{ listing.source_name }}</span>
                </div>
              </div>
              <div class="flex gap-2 flex-shrink-0">
                <a
                  v-if="listing.source_url"
                  :href="listing.source_url"
                  target="_blank"
                  rel="noopener"
                  class="btn-secondary text-sm"
                >
                  🔗
                </a>
                <button class="btn-ghost" @click="emit('update:modelValue', false)">✕</button>
              </div>
            </div>

            <!-- Scrollable body -->
            <div class="overflow-y-auto flex-1 p-4 space-y-6">
              <!-- Image carousel -->
              <div v-if="listing.images?.length" class="relative">
                <div class="aspect-video bg-gray-100 rounded-xl overflow-hidden">
                  <img
                    :src="listing.images[currentImage]"
                    :alt="listing.title"
                    class="w-full h-full object-cover"
                  />
                </div>
                <div v-if="listing.images.length > 1" class="flex gap-1 mt-2 overflow-x-auto pb-1">
                  <button
                    v-for="(img, i) in listing.images"
                    :key="i"
                    class="flex-shrink-0 w-14 h-10 rounded overflow-hidden border-2 transition-colors"
                    :class="i === currentImage ? 'border-indigo-500' : 'border-transparent'"
                    @click="currentImage = i"
                  >
                    <img :src="img" class="w-full h-full object-cover" />
                  </button>
                </div>
              </div>

              <!-- Dati principali -->
              <section>
                <h3 class="section-title">📋 Dati principali</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Anno</dt><dd>{{ listing.year ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Prezzo</dt><dd>{{ formatPrice(listing.price) }}</dd></div>
                  <div class="detail-row"><dt>Chilometri</dt><dd>{{ formatKm(listing.mileage_km) }}</dd></div>
                  <div class="detail-row"><dt>Marca</dt><dd>{{ listing.brand ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Modello</dt><dd>{{ listing.model ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Versione</dt><dd>{{ listing.version ?? ndash }}</dd></div>
                </dl>
              </section>

              <!-- Motore -->
              <section>
                <h3 class="section-title">⚙️ Motore</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Carburante</dt><dd>{{ listing.fuel_type ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Cambio</dt><dd>{{ listing.transmission ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Potenza</dt><dd>{{ listing.engine_power_kw ? listing.engine_power_kw + ' kW' : ndash }}</dd></div>
                  <div class="detail-row"><dt>Cilindrata</dt><dd>{{ listing.engine_displacement_cc ? listing.engine_displacement_cc + ' cc' : ndash }}</dd></div>
                  <div class="detail-row"><dt>Emissioni</dt><dd>{{ listing.emission_class ?? ndash }}</dd></div>
                </dl>
              </section>

              <!-- Dimensioni -->
              <section>
                <h3 class="section-title">📐 Dimensioni</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Lunghezza</dt><dd>{{ listing.length_mm ? (listing.length_mm / 1000).toFixed(2) + ' m' : ndash }}</dd></div>
                  <div class="detail-row"><dt>Larghezza</dt><dd>{{ listing.width_mm ? (listing.width_mm / 1000).toFixed(2) + ' m' : ndash }}</dd></div>
                  <div class="detail-row"><dt>Altezza</dt><dd>{{ listing.height_mm ? (listing.height_mm / 1000).toFixed(2) + ' m' : ndash }}</dd></div>
                  <div class="detail-row"><dt>Massa</dt><dd>{{ listing.mass_kg ? listing.mass_kg + ' kg' : ndash }}</dd></div>
                </dl>
              </section>

              <!-- Configurazione -->
              <section>
                <h3 class="section-title">🏕️ Configurazione</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Tipo carrozzeria</dt><dd>{{ listing.layout_type ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Posti viaggio</dt><dd>{{ listing.seats_travel ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Posti letto</dt><dd>{{ listing.seats_sleeping ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Tipi letto</dt><dd>{{ listing.bed_types?.join(', ') ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Patente</dt><dd>{{ listing.driving_license_category ?? ndash }}</dd></div>
                </dl>
              </section>

              <!-- Dotazioni -->
              <section>
                <h3 class="section-title">🔧 Dotazioni</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Garage posteriore</dt><dd>{{ boolLabel(listing.has_rear_garage) }}</dd></div>
                  <div class="detail-row"><dt>Dimensione garage</dt><dd>{{ listing.garage_size_category ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Letti a castello</dt><dd>{{ boolLabel(listing.has_bunk_beds) }}</dd></div>
                  <div class="detail-row"><dt>Doppio pavimento</dt><dd>{{ boolLabel(listing.has_double_floor) }}</dd></div>
                  <div class="detail-row"><dt>Bagno</dt><dd>{{ listing.bathroom_type ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Riscaldamento</dt><dd>{{ listing.heating_type ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Aria condizionata</dt><dd>{{ boolLabel(listing.air_conditioning) }}</dd></div>
                  <div class="detail-row"><dt>Pannello solare</dt><dd>{{ boolLabel(listing.solar_panel) }}</dd></div>
                  <div class="detail-row"><dt>Gancio traino</dt><dd>{{ boolLabel(listing.tow_bar) }}</dd></div>
                </dl>
              </section>

              <!-- Venditore -->
              <section>
                <h3 class="section-title">👤 Venditore</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Nome</dt><dd>{{ listing.seller_name ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Tipo</dt><dd>{{ sellerTypeLabel }}</dd></div>
                </dl>
              </section>

              <!-- Posizione -->
              <section>
                <h3 class="section-title">📍 Posizione</h3>
                <dl class="detail-grid">
                  <div class="detail-row"><dt>Indirizzo</dt><dd>{{ listing.address_raw ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Città</dt><dd>{{ listing.city ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Provincia</dt><dd>{{ listing.province ?? ndash }}</dd></div>
                  <div class="detail-row"><dt>Regione</dt><dd>{{ listing.region ?? ndash }}</dd></div>
                </dl>
              </section>

              <!-- Descrizione -->
              <section v-if="listing.description_raw">
                <h3 class="section-title">📝 Descrizione</h3>
                <div class="bg-gray-50 rounded-lg p-3 text-sm text-gray-700 whitespace-pre-line max-h-64 overflow-y-auto">
                  {{ listing.description_raw }}
                </div>
              </section>

              <!-- Qualità dati -->
              <section>
                <h3 class="section-title">📊 Qualità dati</h3>
                <div class="space-y-2">
                  <div>
                    <div class="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Estrazione</span>
                      <span>{{ pct(listing.extraction_confidence) }}%</span>
                    </div>
                    <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all"
                        :class="confidenceColor(listing.extraction_confidence)"
                        :style="{ width: pct(listing.extraction_confidence) + '%' }"
                      />
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Arricchimento</span>
                      <span>{{ pct(listing.enrichment_confidence) }}%</span>
                    </div>
                    <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        class="h-full rounded-full transition-all"
                        :class="confidenceColor(listing.enrichment_confidence)"
                        :style="{ width: pct(listing.enrichment_confidence) + '%' }"
                      />
                    </div>
                  </div>
                </div>
              </section>

              <!-- Features -->
              <section v-if="listing.features?.length">
                <h3 class="section-title">🏷️ Caratteristiche aggiuntive</h3>
                <div class="flex flex-wrap gap-2">
                  <div
                    v-for="f in listing.features"
                    :key="f.feature_key"
                    class="pill flex items-center gap-1"
                  >
                    <span>{{ f.feature_key }}</span>
                    <span v-if="f.value" class="font-semibold">: {{ f.value }}</span>
                  </div>
                </div>
              </section>
            </div>

            <!-- Footer actions -->
            <div class="p-4 border-t border-gray-100 flex gap-2 flex-shrink-0">
              <button class="btn-danger text-sm" @click="handleMarkSold">
                🏷️ Segna come venduto
              </button>
              <button class="btn-secondary text-sm ml-auto" @click="emit('update:modelValue', false)">
                Chiudi
              </button>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Listing } from '../types/listing'
import { fetchListing, markSold } from '../api/listings'

const props = defineProps<{
  modelValue: boolean
  listingId: number | null
}>()

const emit = defineEmits<{
  'update:modelValue': [val: boolean]
  sold: [id: number]
}>()

const listing = ref<Listing | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const currentImage = ref(0)
const ndash = '—'

async function load() {
  if (!props.listingId) return
  loading.value = true
  error.value = null
  try {
    listing.value = await fetchListing(props.listingId)
    currentImage.value = 0
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Errore caricamento'
  } finally {
    loading.value = false
  }
}

watch(() => props.listingId, (id) => { if (id && props.modelValue) load() })
watch(() => props.modelValue, (open) => { if (open && props.listingId) load() })

async function handleMarkSold() {
  if (!listing.value) return
  if (!confirm('Sei sicuro di voler segnare questo annuncio come venduto?')) return
  try {
    await markSold(listing.value.id)
    emit('sold', listing.value.id)
    emit('update:modelValue', false)
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Errore')
  }
}

function formatPrice(price: number | null): string {
  if (price === null) return '—'
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(price)
}

function formatKm(km: number | null): string {
  if (km === null) return '—'
  return new Intl.NumberFormat('it-IT').format(km) + ' km'
}

function boolLabel(val: boolean | null): string {
  if (val === null || val === undefined) return '—'
  return val ? 'Sì' : 'No'
}

const sellerTypeLabel = computed(() => {
  if (!listing.value) return '—'
  if (listing.value.seller_type === 'dealer') return 'Concessionario'
  if (listing.value.seller_type === 'private') return 'Privato'
  return listing.value.seller_type ?? '—'
})

function pct(val: number | null): number {
  return Math.round((val ?? 0) * 100)
}

function confidenceColor(val: number | null): string {
  if (val === null) return 'bg-gray-300'
  if (val >= 0.8) return 'bg-green-500'
  if (val >= 0.5) return 'bg-amber-400'
  return 'bg-red-400'
}
</script>

<script lang="ts">
import { computed } from 'vue'
</script>

<style scoped>
@reference "tailwindcss";

.section-title {
  @apply text-sm font-semibold text-gray-700 mb-2 pb-1 border-b border-gray-100;
}

.detail-grid {
  @apply grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-2;
}

.detail-row dt {
  @apply text-xs text-gray-400 font-medium;
}

.detail-row dd {
  @apply text-sm text-gray-800;
}
</style>

<style>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
