<script setup>
import AppIcon from './AppIcon.vue'

defineProps({
  icon: String,
  variant: { type: String, default: 'ghost' } // ghost | primary
})
</script>

<template>
  <button
    class="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition"
    :class="variant === 'primary'
      ? 'bg-blue-600 text-white hover:bg-blue-700'
      : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'"
  >
    <AppIcon v-if="icon" :name="icon" class="h-4 w-4" />
    <slot />
  </button>
</template>
