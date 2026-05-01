<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-800">📡 Sorgenti dati</h2>
      <button class="btn-primary text-sm" @click="showForm = true">+ Aggiungi</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-10">
      <div class="animate-spin rounded-full h-8 w-8 border-4 border-indigo-200 border-t-indigo-600" />
    </div>

    <!-- Empty -->
    <div v-else-if="!sources.length" class="text-center py-10 text-gray-400">
      <p class="text-3xl mb-2">📭</p>
      <p>Nessuna sorgente configurata</p>
    </div>

    <!-- Sources list -->
    <div v-else class="space-y-3">
      <div v-for="s in sources" :key="s.id" class="card p-4 flex items-center gap-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <span class="font-semibold text-gray-800">{{ s.name }}</span>
            <span :class="s.is_active ? 'badge-green' : 'badge-gray'">
              {{ s.is_active ? 'Attiva' : 'Disattiva' }}
            </span>
            <span class="badge-blue">{{ s.source_type }}</span>
          </div>
          <div class="text-xs text-gray-400 flex gap-3 flex-wrap">
            <span v-if="s.base_url">🔗 {{ s.base_url }}</span>
            <span v-if="s.last_scraped_at">🕐 {{ formatDate(s.last_scraped_at) }}</span>
            <span v-if="s.listing_count !== undefined">📊 {{ s.listing_count }} annunci</span>
          </div>
        </div>
        <div class="flex gap-2 flex-shrink-0">
          <button class="btn-ghost text-xs" @click="editSource(s)">✏️</button>
          <button class="btn-ghost text-xs text-red-500 hover:text-red-700 hover:bg-red-50" @click="handleDelete(s.id)">🗑️</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit form modal -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-5">
        <h3 class="font-bold text-gray-900 mb-4">{{ editingId ? 'Modifica sorgente' : 'Nuova sorgente' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="label">Nome *</label>
            <input v-model="formData.name" class="input" placeholder="es. Subito.it" />
          </div>
          <div>
            <label class="label">Tipo *</label>
            <select v-model="formData.source_type" class="input">
              <option value="scraper">Scraper</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="api">API</option>
              <option value="manual">Manuale</option>
            </select>
          </div>
          <div>
            <label class="label">URL base</label>
            <input v-model="formData.base_url" class="input" placeholder="https://..." />
          </div>
          <div>
            <label class="label">Intervallo scraping (ore)</label>
            <input v-model.number="formData.scrape_interval_hours" type="number" class="input" min="1" />
          </div>
          <div class="flex items-center gap-2">
            <input type="checkbox" id="is_active" v-model="formData.is_active" class="rounded" />
            <label for="is_active" class="text-sm text-gray-700">Attiva</label>
          </div>
        </div>
        <div class="flex gap-2 mt-5">
          <button class="btn-primary flex-1" :disabled="saving" @click="handleSave">
            {{ saving ? '...' : (editingId ? 'Salva' : 'Crea') }}
          </button>
          <button class="btn-secondary" @click="closeForm">Annulla</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import type { Source } from '../types/source'
import { fetchSources, createSource, updateSource, deleteSource } from '../api/sources'

const sources = ref<Source[]>([])
const loading = ref(false)
const showForm = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)

const formData = reactive({
  name: '',
  source_type: 'scraper',
  base_url: '',
  is_active: true,
  scrape_interval_hours: 24,
})

async function load() {
  loading.value = true
  try {
    sources.value = await fetchSources()
  } finally {
    loading.value = false
  }
}

onMounted(load)

function editSource(s: Source) {
  editingId.value = s.id
  formData.name = s.name
  formData.source_type = s.source_type
  formData.base_url = s.base_url ?? ''
  formData.is_active = s.is_active
  formData.scrape_interval_hours = s.scrape_interval_hours ?? 24
  showForm.value = true
}

async function handleSave() {
  if (!formData.name) return alert('Nome obbligatorio')
  saving.value = true
  try {
    if (editingId.value) {
      await updateSource(editingId.value, { ...formData })
    } else {
      await createSource({ ...formData })
    }
    await load()
    closeForm()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Errore')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Eliminare questa sorgente?')) return
  try {
    await deleteSource(id)
    await load()
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Errore')
  }
}

function closeForm() {
  showForm.value = false
  editingId.value = null
  formData.name = ''
  formData.source_type = 'scraper'
  formData.base_url = ''
  formData.is_active = true
  formData.scrape_interval_hours = 24
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
</script>
