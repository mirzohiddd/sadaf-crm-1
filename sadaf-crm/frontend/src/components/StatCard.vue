<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  label: String,
  value: String,
  delta: String,
  period: String,
  icon: String,
  color: { type: String, default: 'blue' }
})

const tones = {
  blue:   'bg-blue-500',
  green:  'bg-emerald-500',
  amber:  'bg-amber-500',
  violet: 'bg-violet-500',
  teal:   'bg-teal-500'
}
</script>

<template>
  <div class="card lift p-4 flex items-center gap-4">
    <div :class="[tones[color], 'shrink-0 grid h-12 w-12 place-items-center rounded-xl text-white']">
      <AppIcon :name="icon" class="h-6 w-6" />
    </div>
    <div class="min-w-0">
      <p class="text-xs text-slate-500">{{ label }}</p>
      <p class="mt-0.5 text-2xl font-bold text-slate-900 leading-tight">{{ value }}</p>
      <p class="mt-0.5 flex items-center gap-2 text-xs">
        <span class="font-semibold text-emerald-600">{{ delta }}</span>
        <span class="text-slate-400">{{ period }}</span>
      </p>
    </div>
  </div>
</template>
