<script setup>
import AppIcon from './AppIcon.vue'
defineProps({
  label: String,
  value: [String, Number],
  unit: String,
  note: String,
  noteTone: { type: String, default: 'muted' },
  icon: String,
  color: { type: String, default: 'blue' }
})
const tones = {
  blue: 'bg-blue-500', green: 'bg-emerald-500', amber: 'bg-amber-500',
  violet: 'bg-violet-500', teal: 'bg-teal-500', rose: 'bg-rose-500',
  sky: 'bg-sky-500', indigo: 'bg-indigo-500'
}
const noteTones = { muted: 'text-slate-400', up: 'text-emerald-600', down: 'text-rose-500', warn: 'text-amber-600' }
</script>
<template>
  <div class="card lift p-4">
    <div class="flex items-start gap-3.5">
      <span :class="[tones[color], 'grid h-11 w-11 shrink-0 place-items-center rounded-xl text-white']">
        <AppIcon :name="icon" class="h-5 w-5" />
      </span>
      <div class="min-w-0">
        <p class="text-xs text-slate-500">{{ label }}</p>
        <p class="mt-0.5 flex items-baseline gap-1.5">
          <span class="text-2xl font-bold leading-tight text-slate-900">{{ value }}</span>
          <span v-if="unit" class="text-sm text-slate-500">{{ unit }}</span>
        </p>
        <p v-if="note" class="mt-0.5 text-xs" :class="noteTones[noteTone]">{{ note }}</p>
      </div>
    </div>
  </div>
</template>
