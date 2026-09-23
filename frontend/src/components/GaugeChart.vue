<script setup>
import { computed } from 'vue'
const props = defineProps({
  value: { type: Number, default: 0 },
  target: { type: Number, default: 100 },
  label: String,
  format: { type: Function, default: (n) => String(n) }
})
const R = 70
const CX = 100
const CY = 100
const ratio = computed(() => Math.min(1, props.target ? props.value / props.target : 0))
const ARC = Math.PI * R
const arcPath = `M ${CX - R} ${CY} A ${R} ${R} 0 0 1 ${CX + R} ${CY}`
const tone = computed(() =>
  ratio.value >= 0.8 ? '#10b981' : ratio.value >= 0.4 ? '#3b82f6' : '#f59e0b'
)
</script>

<template>
  <div class="flex flex-col items-center">
    <svg viewBox="0 0 200 120" class="w-full max-w-[220px]" role="img" :aria-label="label">
      <path :d="arcPath" fill="none" stroke="#e2e8f0" stroke-width="16" stroke-linecap="round" />
      <path :d="arcPath" fill="none" :stroke="tone" stroke-width="16" stroke-linecap="round"
            :stroke-dasharray="`${ratio * ARC} ${ARC}`" style="transition: stroke-dasharray .6s ease" />

      <text x="100" y="92" text-anchor="middle" class="fill-slate-900 text-[22px] font-bold">
        {{ Math.round(ratio * 100) }}%
      </text>
    </svg>

    <div class="mt-1 flex w-full max-w-[220px] justify-between text-xs text-slate-500">
      <span>{{ format(value) }}</span>
      <span>{{ format(target) }}</span>
    </div>
    <p v-if="label" class="mt-1 text-xs text-slate-400">{{ label }}</p>
  </div>
</template>
