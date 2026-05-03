<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">📥 Importa annunci</h1>

    <!-- Format tabs -->
    <div class="flex gap-1 mb-6 bg-gray-100 rounded-xl p-1 w-fit">
      <button
        v-for="fmt in (['csv', 'json'] as const)"
        :key="fmt"
        class="px-5 py-2 rounded-lg text-sm font-medium transition-all"
        :class="format === fmt ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
        @click="format = fmt; reset()"
      >
        {{ fmt.toUpperCase() }}
      </button>
    </div>

    <!-- Dropzone -->
    <div
      v-if="!preview"
      class="border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer"
      :class="dragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-gray-400'"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <div class="text-5xl mb-3">📁</div>
      <p class="text-gray-600 font-medium">Trascina qui il file {{ format.toUpperCase() }}</p>
      <p class="text-sm text-gray-400 mt-1">oppure clicca per selezionare</p>
      <input ref="fileInput" type="file" :accept="format === 'csv' ? '.csv' : '.json'" class="hidden" @change="onFileChange" />
    </div>

    <!-- Loading preview -->
    <div v-if="loadingPreview" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-4 border-indigo-200 border-t-indigo-600 mr-3" />
      <span class="text-gray-600">Analisi file in corso...</span>
    </div>

    <!-- Preview result -->
    <div v-if="preview && !importResult" class="space-y-5">
      <div class="card p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-800">📋 Anteprima file</h3>
          <button class="btn-ghost text-sm" @click="reset">✕ Cambia file</button>
        </div>

        <div class="flex gap-4 text-sm text-gray-600 mb-4">
          <span>📄 File: <strong>{{ selectedFile?.name }}</strong></span>
          <span>📊 Righe: <strong>{{ preview.total_rows }}</strong></span>
        </div>

        <!-- Warnings -->
        <div v-if="preview.warnings.length" class="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-200">
          <p class="text-xs font-semibold text-amber-700 mb-1">⚠️ Avvisi</p>
          <ul class="list-disc list-inside text-xs text-amber-600 space-y-0.5">
            <li v-for="w in preview.warnings" :key="w">{{ w }}</li>
          </ul>
        </div>

        <!-- Column mapping -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-2">Mappatura colonne</h4>
          <div class="overflow-x-auto">
            <table class="w-full text-xs border-collapse">
              <thead>
                <tr class="bg-gray-50">
                  <th class="text-left px-3 py-2 font-semibold text-gray-500 border-b">Colonna file</th>
                  <th class="text-left px-3 py-2 font-semibold text-gray-500 border-b">Campo destinazione</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="col in preview.detected_columns" :key="col" class="border-b border-gray-50">
                  <td class="px-3 py-2 font-mono text-gray-700">{{ col }}</td>
                  <td class="px-3 py-2">
                    <select
                      v-model="columnMapping[col]"
                      class="input text-xs py-1"
                    >
                      <option value="">(ignora)</option>
                      <option v-for="f in listingFields" :key="f.key" :value="f.key">{{ f.label }}</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Preview rows -->
        <div class="mt-4">
          <h4 class="text-sm font-semibold text-gray-700 mb-2">Prime righe</h4>
          <div class="overflow-x-auto rounded-lg border border-gray-200">
            <table class="w-full text-xs">
              <thead class="bg-gray-50">
                <tr>
                  <th
                    v-for="col in preview.detected_columns.slice(0, 8)"
                    :key="col"
                    class="px-3 py-2 text-left font-semibold text-gray-500 whitespace-nowrap"
                  >{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, i) in preview.preview_rows.slice(0, 10)"
                  :key="i"
                  class="border-t border-gray-100 hover:bg-gray-50"
                >
                  <td
                    v-for="col in preview.detected_columns.slice(0, 8)"
                    :key="col"
                    class="px-3 py-1.5 text-gray-700 max-w-[140px] truncate"
                  >
                    {{ row[col] ?? '' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <button
        class="btn-primary w-full text-base py-3"
        :disabled="loadingImport"
        @click="confirmImport"
      >
        <span v-if="loadingImport">
          <span class="animate-spin inline-block mr-2">⏳</span> Importazione...
        </span>
        <span v-else>✅ Conferma importazione</span>
      </button>
    </div>

    <!-- Import result -->
    <div v-if="importResult" class="card p-6 text-center space-y-4">
      <div class="text-5xl">🎉</div>
      <h3 class="text-xl font-bold text-gray-900">Importazione completata</h3>
      <div class="flex justify-center gap-6 flex-wrap">
        <div class="text-center">
          <div class="text-3xl font-bold text-green-600">{{ importResult.imported }}</div>
          <div class="text-xs text-gray-500">Importati</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-amber-500">{{ importResult.skipped }}</div>
          <div class="text-xs text-gray-500">Saltati</div>
        </div>
        <div class="text-center">
          <div class="text-3xl font-bold text-red-500">{{ importResult.errors }}</div>
          <div class="text-xs text-gray-500">Errori</div>
        </div>
      </div>
      <div v-if="importResult.error_messages?.length" class="text-left bg-red-50 rounded-lg p-3">
        <p class="text-xs font-semibold text-red-700 mb-1">Messaggi di errore:</p>
        <ul class="list-disc list-inside text-xs text-red-600 space-y-0.5 max-h-32 overflow-y-auto">
          <li v-for="m in importResult.error_messages" :key="m">{{ m }}</li>
        </ul>
      </div>
      <button class="btn-primary" @click="reset">📥 Nuova importazione</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { previewImport, confirmImport as apiConfirmImport } from '../api/imports'
import type { ImportPreviewResult, ImportResult } from '../types/import'

const format = ref<'csv' | 'json'>('csv')
const dragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const preview = ref<ImportPreviewResult | null>(null)
const importResult = ref<ImportResult | null>(null)
const loadingPreview = ref(false)
const loadingImport = ref(false)
const columnMapping = reactive<Record<string, string>>({})

const listingFields = [
  { key: 'title', label: 'Titolo' },
  { key: 'brand', label: 'Marca' },
  { key: 'model', label: 'Modello' },
  { key: 'year', label: 'Anno' },
  { key: 'price', label: 'Prezzo' },
  { key: 'mileage_km', label: 'Chilometri' },
  { key: 'fuel_type', label: 'Carburante' },
  { key: 'transmission', label: 'Cambio' },
  { key: 'layout_type', label: 'Tipo carrozzeria' },
  { key: 'city', label: 'Città' },
  { key: 'province', label: 'Provincia' },
  { key: 'region', label: 'Regione' },
  { key: 'seller_name', label: 'Venditore' },
  { key: 'seller_type', label: 'Tipo venditore' },
  { key: 'source_url', label: 'URL annuncio' },
  { key: 'description_raw', label: 'Descrizione' },
]

function onDrop(e: DragEvent) {
  dragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) processFile(file)
}

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) processFile(file)
}

async function processFile(file: File) {
  selectedFile.value = file
  loadingPreview.value = true
  try {
    const result = await previewImport(file, format.value)
    preview.value = result
    Object.keys(columnMapping).forEach((k) => delete columnMapping[k])
    result.detected_columns.forEach((col) => {
      columnMapping[col] = result.column_mapping[col] ?? ''
    })
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Errore anteprima')
  } finally {
    loadingPreview.value = false
  }
}

async function confirmImport() {
  if (!selectedFile.value) return
  loadingImport.value = true
  try {
    importResult.value = await apiConfirmImport(selectedFile.value, format.value, { ...columnMapping })
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Errore importazione')
  } finally {
    loadingImport.value = false
  }
}

function reset() {
  selectedFile.value = null
  preview.value = null
  importResult.value = null
  if (fileInput.value) fileInput.value.value = ''
}
</script>
