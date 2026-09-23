<script setup>
import { computed } from 'vue'
const props = defineProps({
  data: { type: Array, required: true }, 
  centerLabel: { type: String, default: 'Jami' }
})
const total = computed(() => props.data.reduce((s, d) => s + d.value, 0))
const R = 60
const C = 2 * Math.PI * R
const segments = computed(() => {
  let offset = 0
  return props.data.map((d) => {
    const share = total.value ? d.value / total.value : 0
    const seg = {
      color: d.color,
      dash: `${share * C - 3} ${C - share * C + 3}`,
      offset: -offset * C
    }
    offset += share
    return seg
  })
})
const percent = (v) => (total.value ? Math.round((v / total.value) * 100) : 0)
</script>
<template>
  <div v-if="!data.length" class="py-10 text-center text-sm text-slate-400">Ma'lumot yo'q</div>
  <div v-else class="flex flex-col items-center gap-6 sm:flex-row sm:justify-around">
    <svg viewBox="0 0 160 160" class="h-40 w-40 -rotate-90">
      <circle
        v-for="(s, i) in segments" :key="i"
        cx="80" cy="80" :r="R"
        fill="none" :stroke="s.color" stroke-width="26"
        :stroke-dasharray="s.dash" :stroke-dashoffset="s.offset"
        stroke-linecap="butt"
      />
      <g class="rotate-90" style="transform-origin: 80px 80px">
        <text x="80" y="76" text-anchor="middle" class="fill-slate-900 text-[22px] font-bold">{{ total }}</text>
        <text x="80" y="94" text-anchor="middle" class="fill-slate-400 text-[11px]">{{ centerLabel }}</text>
      </g>
    </svg>
    <ul class="w-full max-w-[200px] space-y-3">
      <li v-for="d in data" :key="d.label" class="flex items-center gap-2 text-sm">
        <span class="h-2.5 w-2.5 rounded-full" :style="{ background: d.color }" />
        <span class="text-slate-600">{{ d.label }}</span>
        <span class="ml-auto text-slate-500">{{ d.value }} ({{ percent(d.value) }}%)</span>
      </li>
    </ul>
  </div>
</template>
