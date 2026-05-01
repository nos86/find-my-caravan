<template>
  <div class="flex flex-col gap-4">
    <!-- Search -->
    <div>
      <label class="label">Ricerca libera</label>
      <input
        v-model="local.q"
        type="text"
        placeholder="Cerca per titolo, descrizione..."
        class="input"
        @input="debouncedEmit"
      />
    </div>

    <!-- Tipo veicolo -->
    <div>
      <label class="label">Tipo veicolo</label>
      <select v-model="local.vehicle_type" class="input" @change="emitFilters">
        <option value="">Tutti</option>
        <option value="mansardato">Mansardato</option>
        <option value="semintegrale">Semintegrale</option>
        <option value="motorhome">Motorhome</option>
        <option value="furgonato">Furgonato</option>
        <option value="campervan">Campervan</option>
      </select>
    </div>

    <!-- Prezzo -->
    <div>
      <label class="label">Prezzo (€)</label>
      <div class="flex gap-2">
        <input v-model.number="local.price_min" type="number" placeholder="Min" class="input" min="0" @change="emitFilters" />
        <input v-model.number="local.price_max" type="number" placeholder="Max" class="input" min="0" @change="emitFilters" />
      </div>
    </div>

    <!-- Anno -->
    <div>
      <label class="label">Anno immatricolazione</label>
      <div class="flex gap-2">
        <input v-model.number="local.year_min" type="number" placeholder="Da" class="input" min="1980" :max="currentYear" @change="emitFilters" />
        <input v-model.number="local.year_max" type="number" placeholder="A" class="input" min="1980" :max="currentYear" @change="emitFilters" />
      </div>
    </div>

    <!-- Km max -->
    <div>
      <label class="label">Km max</label>
      <input v-model.number="local.mileage_max" type="number" placeholder="es. 100000" class="input" min="0" @change="emitFilters" />
    </div>

    <!-- Marca -->
    <div>
      <label class="label">Marca</label>
      <input v-model="local.brand" type="text" placeholder="es. Fiat, Knaus..." class="input" @input="debouncedEmit" />
    </div>

    <!-- Regione -->
    <div>
      <label class="label">Regione</label>
      <select v-model="local.region" class="input" @change="emitFilters">
        <option value="">Tutte</option>
        <option v-for="r in italianRegions" :key="r" :value="r">{{ r }}</option>
      </select>
    </div>

    <!-- Venditore -->
    <div>
      <label class="label">Venditore</label>
      <select v-model="local.seller_type" class="input" @change="emitFilters">
        <option value="">Tutti</option>
        <option value="private">Privato</option>
        <option value="dealer">Concessionario</option>
      </select>
    </div>

    <!-- Dotazioni -->
    <div>
      <label class="label">Dotazioni</label>
      <div class="space-y-1.5">
        <label v-for="feat in featureOptions" :key="feat.key" class="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            :value="feat.key"
            v-model="localFeatures"
            class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            @change="emitFilters"
          />
          <span class="text-sm text-gray-700">{{ feat.label }}</span>
        </label>
      </div>
    </div>

    <!-- Ordina per -->
    <div>
      <label class="label">Ordina per</label>
      <select v-model="local.sort_by" class="input" @change="emitFilters">
        <option value="">Rilevanza</option>
        <option value="price_asc">Prezzo crescente</option>
        <option value="price_desc">Prezzo decrescente</option>
        <option value="year_desc">Anno (più recente)</option>
        <option value="year_asc">Anno (più vecchio)</option>
        <option value="mileage_asc">Km crescente</option>
        <option value="date_desc">Data inserimento</option>
      </select>
    </div>

    <!-- Actions -->
    <div class="flex gap-2 pt-2 border-t border-gray-100">
      <button class="btn-primary flex-1" @click="emitFilters">
        🔍 Cerca
      </button>
      <button class="btn-secondary" @click="resetFilters" title="Reset filtri">
        ✕
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import type { ListingFilters } from '../types/listing'

const props = defineProps<{ modelValue: ListingFilters }>()
const emit = defineEmits<{
  'update:modelValue': [filters: ListingFilters]
  search: []
}>()

const currentYear = new Date().getFullYear()

const italianRegions = [
  'Abruzzo', 'Basilicata', 'Calabria', 'Campania', 'Emilia-Romagna',
  'Friuli-Venezia Giulia', 'Lazio', 'Liguria', 'Lombardia', 'Marche',
  'Molise', 'Piemonte', 'Puglia', 'Sardegna', 'Sicilia', 'Toscana',
  'Trentino-Alto Adige', 'Umbria', "Valle d'Aosta", 'Veneto',
]

const featureOptions = [
  { key: 'garage_grande', label: 'Garage grande' },
  { key: 'letti_castello', label: 'Letti a castello' },
  { key: 'letto_matrimoniale_posteriore', label: 'Letto matrimoniale post.' },
  { key: 'doppio_pavimento', label: 'Doppio pavimento' },
  { key: 'aria_condizionata', label: 'Aria condizionata' },
  { key: 'pannello_solare', label: 'Pannello solare' },
  { key: 'patente_b', label: 'Patente B' },
]

const local = reactive<ListingFilters>({ ...props.modelValue })
const localFeatures = ref<string[]>([...(props.modelValue.features ?? [])])

watch(() => props.modelValue, (val) => {
  Object.assign(local, val)
  localFeatures.value = [...(val.features ?? [])]
})

function emitFilters() {
  emit('update:modelValue', { ...local, features: localFeatures.value.length ? localFeatures.value : undefined })
  emit('search')
}

const debouncedEmit = useDebounceFn(emitFilters, 500)

function resetFilters() {
  Object.keys(local).forEach((k) => {
    (local as Record<string, unknown>)[k] = undefined
  })
  localFeatures.value = []
  emitFilters()
}
</script>
