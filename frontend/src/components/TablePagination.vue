<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  page: { type: Number, required: true },
  total: { type: Number, required: true },
  perPage: { type: Number, default: 6 },
  summary: String
})
const emit = defineEmits(['update:page'])

const pages = computed(() => Math.max(1, Math.ceil(props.total / props.perPage)))
const list = computed(() => Array.from({ length: pages.value }, (_, i) => i + 1))

const go = (p) => {
  if (p >= 1 && p <= pages.value) emit('update:page', p)
}
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 px-5 py-4">
    <p class="text-sm text-slate-500">{{ summary }}</p>

    <nav class="flex items-center gap-1.5" aria-label="Sahifalar">
      <button class="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 text-slate-500 disabled:opacity-40 hover:bg-slate-50"
              :disabled="page === 1" aria-label="Oldingi" @click="go(page - 1)">
        <AppIcon name="chevron" class="h-4 w-4 rotate-90" />
      </button>

      <button v-for="p in list" :key="p"
              class="h-9 min-w-9 rounded-lg border px-3 text-sm font-medium"
              :class="p === page ? 'border-blue-600 bg-blue-600 text-white' : 'border-slate-200 text-slate-600 hover:bg-slate-50'"
              @click="go(p)">{{ p }}</button>

      <button class="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 text-slate-500 disabled:opacity-40 hover:bg-slate-50"
              :disabled="page === pages" aria-label="Keyingi" @click="go(page + 1)">
        <AppIcon name="chevron" class="h-4 w-4 -rotate-90" />
      </button>
    </nav>
  </div>
</template>
