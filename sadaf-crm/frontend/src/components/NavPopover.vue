<script setup>
import { onMounted, onUnmounted } from 'vue'

defineProps({
  title: String,
  width: { type: String, default: 'w-[360px]' }
})
const emit = defineEmits(['close'])

function onKey(e) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <!-- Tashqariga bosilganda yopish uchun ko'rinmas qatlam -->
  <div class="fixed inset-0 z-40" @click="$emit('close')" />

  <div
    class="animate-pop-in absolute right-0 z-50 mt-2 max-h-[80vh] overflow-y-auto rounded-2xl border border-slate-100 bg-white shadow-2xl max-sm:fixed max-sm:inset-x-3 max-sm:top-[68px] max-sm:!w-auto"
    :class="width"
    role="dialog"
    @click.stop
  >
    <header v-if="title || $slots.header" class="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">
      <slot name="header">
        <h2 class="text-sm font-semibold text-slate-900">{{ title }}</h2>
      </slot>
      <slot name="action" />
    </header>

    <slot />
  </div>
</template>
