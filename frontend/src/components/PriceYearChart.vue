<template>
  <div class="w-full">
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="animate-spin rounded-full h-10 w-10 border-4 border-indigo-200 border-t-indigo-600" />
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-96 gap-2 text-red-500">
      <span class="text-3xl">⚠️</span>
      <p>{{ error }}</p>
    </div>
    <div v-else-if="!chartData" class="flex items-center justify-center h-96 text-gray-400">
      Nessun dato disponibile
    </div>
    <div v-else>
      <div class="flex items-center gap-3 mb-3 flex-wrap">
        <h3 class="font-semibold text-gray-700 text-sm">Prezzo per anno di immatricolazione</h3>
        <span class="text-xs text-gray-400">({{ points.length }} annunci)</span>
      </div>
      <Scatter :data="chartData" :options="chartOptions" class="max-h-[480px]" @click="handleChartClick" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Scatter } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  type ChartOptions,
  type ChartData,
} from 'chart.js'
import { fetchPriceYear } from '../api/analytics'
import type { PriceYearPoint } from '../types/analytics'

ChartJS.register(LinearScale, PointElement, Tooltip, Legend)

const props = defineProps<{ filters?: object }>()
const emit = defineEmits<{ 'open-detail': [id: number] }>()

const points = ref<PriceYearPoint[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const BRAND_COLORS = [
  '#6366f1', '#f59e0b', '#10b981', '#ef4444', '#3b82f6',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#84cc16',
]

const brandColorMap = computed(() => {
  const brands = [...new Set(points.value.map((p) => p.brand ?? 'Sconosciuto'))]
  const map: Record<string, string> = {}
  brands.forEach((b, i) => { map[b] = BRAND_COLORS[i % BRAND_COLORS.length] })
  return map
})

const chartData = computed<ChartData<'scatter'> | null>(() => {
  if (!points.value.length) return null
  const brands = [...new Set(points.value.map((p) => p.brand ?? 'Sconosciuto'))]
  return {
    datasets: brands.map((brand) => ({
      label: brand,
      data: points.value
        .filter((p) => (p.brand ?? 'Sconosciuto') === brand)
        .map((p) => ({ x: p.year, y: p.price, ...p })),
      backgroundColor: brandColorMap.value[brand] + 'cc',
      pointRadius: 5,
      pointHoverRadius: 8,
    })),
  }
})

const chartOptions = computed<ChartOptions<'scatter'>>(() => ({
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
    tooltip: {
      callbacks: {
        label(ctx) {
          const raw = ctx.raw as PriceYearPoint
          const price = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(raw.price)
          const km = raw.mileage_km ? new Intl.NumberFormat('it-IT').format(raw.mileage_km) + ' km' : 'km N/D'
          return [raw.title, `${price} · ${raw.year} · ${km}`, raw.city ?? '']
        },
      },
    },
  },
  scales: {
    x: {
      title: { display: true, text: 'Anno', font: { size: 12 } },
      ticks: { stepSize: 1 },
    },
    y: {
      title: { display: true, text: 'Prezzo (€)', font: { size: 12 } },
      ticks: {
        callback: (val) =>
          new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(val as number),
      },
    },
  },
}))

function handleChartClick(_event: MouseEvent, elements: { datasetIndex: number; index: number }[]) {
  if (!elements.length || !chartData.value) return
  const { datasetIndex, index } = elements[0]
  const raw = chartData.value.datasets[datasetIndex].data[index] as unknown as PriceYearPoint
  if (raw?.id) emit('open-detail', raw.id)
}

async function load() {
  loading.value = true
  error.value = null
  try {
    points.value = await fetchPriceYear(props.filters)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Errore'
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.filters, load, { deep: true })
</script>
