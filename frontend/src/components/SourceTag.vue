<script setup>
import { computed } from 'vue'

const props = defineProps({ source: String })

const map = {
  Telegram:      { dot: 'bg-sky-500',   text: 'text-slate-600' },
  Instagram:     { dot: 'bg-pink-500',  text: 'text-slate-600' },
  Facebook:      { dot: 'bg-blue-600',  text: 'text-slate-600' },
  Sayt:          { dot: 'bg-emerald-500', text: 'text-slate-600' },
  "Qo'ng'iroq":  { dot: 'bg-amber-500', text: 'text-slate-600' }
}
const tone = computed(() => map[props.source] || { dot: 'bg-slate-400', text: 'text-slate-600' })
</script>

<template>
  <span class="inline-flex items-center gap-1.5 text-xs" :class="tone.text">
    <span class="h-2 w-2 rounded-full" :class="tone.dot" />{{ source }}
  </span>
</template>
