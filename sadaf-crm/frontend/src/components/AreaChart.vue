<script setup>
import { computed } from 'vue'
const props = defineProps({
  points: { type: Array, required: true },
  labels: { type: Array, default: () => [] }
})
const W = 560
const H = 220
const PAD_L = 44
const PAD_B = 26
const PAD_T = 10
const hasData = computed(() => props.points.length > 0)
const max = computed(() => {
  if (!props.points.length) return 1000
  const m = Math.max(...props.points)
  if (m <= 0) return 1000
  const pow = Math.pow(10, Math.floor(Math.log10(m)))
  const step = pow / 2
  return Math.max(Math.ceil(m / step) * step, step)
})
const coords = computed(() => {
  const n = props.points.length
  if (!n) return []
  return props.points.map((p, i) => {
    const x = n === 1 ? (PAD_L + W - 8) / 2 : PAD_L + (i / (n - 1)) * (W - PAD_L - 8)
    const y = PAD_T + (1 - p / max.value) * (H - PAD_T - PAD_B)
    return [x, y]
  })
})
const line = computed(() => {
  const c = coords.value
  if (!c.length) return ''
  if (c.length === 1) return `M${PAD_L},${c[0][1]} L${W - 8},${c[0][1]}`
  return c.map(([x, y], i) => `${i ? 'L' : 'M'}${x},${y}`).join(' ')
})
const area = computed(() => {
  const c = coords.value
  if (!c.length) return ''
  if (c.length === 1) {
    const [x, y] = c[0]
    return `M${PAD_L},${y} L${W - 8},${y} L${W - 8},${H - PAD_B} L${PAD_L},${H - PAD_B} Z`
  }
  return `${line.value} L${c.at(-1)[0]},${H - PAD_B} L${PAD_L},${H - PAD_B} Z`
})
const yTicks = computed(() => {
  const step = max.value / 4
  return [0, 1, 2, 3, 4].map((i) => {
    const v = step * i
    const text = !v ? '0' : v >= 1000 ? `${+(v / 1000).toFixed(1)}k` : String(Math.round(v))
    return { v, y: PAD_T + (1 - v / max.value) * (H - PAD_T - PAD_B), text }
  })
})
</script>
<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Sotuvlar dinamikasi">
    <defs>
      <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.28" />
        <stop offset="100%" stop-color="#3b82f6" stop-opacity="0" />
      </linearGradient>
    </defs>
    <g>
      <line v-for="t in yTicks" :key="t.v" :x1="PAD_L" :x2="W - 8" :y1="t.y" :y2="t.y" stroke="#eef2f7" />
      <text v-for="t in yTicks" :key="'l' + t.v" :x="PAD_L - 10" :y="t.y + 4"
            text-anchor="end" class="fill-slate-400 text-[11px]">{{ t.text }}</text>
    </g>
    <template v-if="hasData">
      <path :d="area" fill="url(#areaFill)" />
      <path :d="line" fill="none" stroke="#2563eb" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" />
      <circle v-for="(c, i) in coords" :key="i" :cx="c[0]" :cy="c[1]" r="2.8" fill="#2563eb" />
    </template>
    <text v-else :x="W / 2" :y="H / 2" text-anchor="middle" class="fill-slate-400 text-[13px]">
      Ma'lumot yo'q
    </text>
    <text v-for="(lab, i) in labels" :key="lab"
          :x="labels.length > 1 ? PAD_L + (i / (labels.length - 1)) * (W - PAD_L - 8) : W / 2" :y="H - 6"
          text-anchor="middle" class="fill-slate-400 text-[11px]">{{ lab }}</text>
  </svg>
</template>
