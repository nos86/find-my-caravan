<template>
  <span
    class="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0"
    :class="dotClass"
    :title="`Affidabilità: ${pct}%`"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ confidence: number | null; size?: 'sm' | 'md' }>()

const pct = computed(() => Math.round((props.confidence ?? 0) * 100))

const dotClass = computed(() => {
  if (props.confidence === null) return 'bg-gray-300'
  if (props.confidence >= 0.8) return 'bg-green-500'
  if (props.confidence >= 0.5) return 'bg-amber-400'
  return 'bg-red-400'
})
</script>
