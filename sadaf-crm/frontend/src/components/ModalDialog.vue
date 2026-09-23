<script setup>
import { watch, onUnmounted } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  open: Boolean,
  title: String,
  wide: { type: Boolean, default: false }
})
const emit = defineEmits(['close', 'submit'])

const onKey = (e) => { if (e.key === 'Escape') emit('close') }

watch(() => props.open, (v) => {
  document.body.style.overflow = v ? 'hidden' : ''
  v ? window.addEventListener('keydown', onKey) : window.removeEventListener('keydown', onKey)
})

onUnmounted(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="open"
           class="fixed inset-0 z-50 flex items-end justify-center overflow-y-auto bg-slate-900/50 backdrop-blur-sm sm:items-center sm:p-4"
           role="dialog" aria-modal="true" @click.self="$emit('close')">
        <div class="modal-panel flex max-h-[92vh] w-full flex-col rounded-t-2xl bg-white shadow-2xl sm:my-auto sm:max-h-[90vh] sm:rounded-2xl"
             :class="wide ? 'sm:max-w-3xl' : 'sm:max-w-2xl'">
          <header class="flex shrink-0 items-center justify-between border-b border-slate-100 px-4 py-4 sm:px-6 sm:py-5">
            <h2 class="text-base font-semibold text-slate-900 sm:text-lg">{{ title }}</h2>
            <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                    aria-label="Yopish" @click="$emit('close')">
              <AppIcon name="close" class="h-5 w-5" />
            </button>
          </header>

          <div class="flex-1 overflow-y-auto px-4 py-4 sm:px-6 sm:py-5">
            <slot />
          </div>

          <footer class="flex shrink-0 gap-3 border-t border-slate-100 px-4 py-3 sm:justify-end sm:px-6 sm:py-4">
            <button class="flex-1 rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 sm:flex-none"
                    @click="$emit('close')">Bekor qilish</button>
            <button class="flex-1 rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 sm:flex-none"
                    @click="$emit('submit')">Saqlash</button>
          </footer>
        </div>
      </div>
    </transition>
  </Teleport>
</template>
