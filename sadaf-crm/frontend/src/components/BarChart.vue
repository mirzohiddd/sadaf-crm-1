<script setup>
import { computed } from 'vue'
const props = defineProps({ data: { type: Array, required: true } }) // [{ label, value }]
const max = computed(() => (props.data.length ? Math.max(...props.data.map((d) => d.value)) : 1))
</script>
<template>
  <p v-if="!data.length" class="py-8 text-center text-sm text-slate-400">Ma'lumot yo'q</p>
  <ul v-else class="space-y-4">
    <li v-for="d in data" :key="d.label" class="flex items-center gap-3">
      <span class="w-20 shrink-0 text-sm text-slate-600">{{ d.label }}</span>
      <span class="h-3 flex-1 overflow-hidden rounded-full bg-slate-100">
        <span class="block h-full rounded-full bg-blue-500" :style="{ width: (d.value / max) * 100 + '%' }" />
      </span>
      <span class="w-10 text-right text-sm font-semibold text-slate-700">{{ d.value }}</span>
    </li>
  </ul>
</template>
