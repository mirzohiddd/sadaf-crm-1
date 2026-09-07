<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Array, required: true }
})
const W = 420
const ROW = 52
const GAP = 6
const MAX_W = 260
const LEFT = 10
const max = computed(() => Math.max(1, ...props.data.map((d) => Number(d.value) || 0)))
const height = computed(() => props.data.length * (ROW + GAP) + 20)
const shapes = computed(() =>
  props.data.map((d, i) => {
    const next = props.data[i + 1]
    const wTop = Math.max(28, (Number(d.value) / max.value) * MAX_W)
    const wBot = next ? Math.max(28, (Number(next.value) / max.value) * MAX_W) : wTop * 0.82
    const y = 10 + i * (ROW + GAP)
    const cx = LEFT + MAX_W / 2
    return {
      label: d.label,
      value: d.value,
      y,
      midY: y + ROW / 2,
      points: [
        `${cx - wTop / 2},${y}`,
        `${cx + wTop / 2},${y}`,
        `${cx + wBot / 2},${y + ROW}`,
        `${cx - wBot / 2},${y + ROW}`
      ].join(' '),
      lineX: cx + wTop / 2
    }
  })
)
const opacity = (i) => 1 - i * 0.11
</script>
<template>
  <p v-if="!data.length" class="py-10 text-center text-sm text-slate-400">Ma'lumot yo'q</p>
  <svg v-else :viewBox="`0 0 ${W} ${height}`" class="w-full" role="img" aria-label="Konversiya voronkasi">
    <g v-for="(s, i) in shapes" :key="s.label">
      <polygon :points="s.points" fill="#3b82f6" :fill-opacity="opacity(i)" />
      <line :x1="s.lineX" :x2="LEFT + MAX_W + 22" :y1="s.midY" :y2="s.midY" stroke="#cbd5e1" />
      <text :x="LEFT + MAX_W + 28" :y="s.midY + 4" class="fill-slate-600 text-[12px]">
        {{ s.label }}
      </text>
      <text :x="LEFT + MAX_W / 2" :y="s.midY + 4" text-anchor="middle"
            class="fill-white text-[12px] font-semibold">{{ s.value }}</text>
    </g>
  </svg>
</template>
