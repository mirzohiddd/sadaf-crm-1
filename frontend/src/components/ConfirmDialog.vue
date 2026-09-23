<script setup>
defineProps({ open: Boolean, title: String, message: String })
defineEmits(['confirm', 'cancel'])
</script>
<template>
  <Teleport to="body">
    <transition name="modal">
    <div v-if="open" class="fixed inset-0 z-[60] grid place-items-center bg-slate-900/40 p-4 backdrop-blur-sm"
         role="alertdialog" aria-modal="true" @click.self="$emit('cancel')">
      <div class="modal-panel w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl">
        <h2 class="text-lg font-semibold text-slate-900">{{ title }}</h2>
        <p class="mt-2 text-sm text-slate-600">{{ message }}</p>
        <div class="mt-6 flex justify-end gap-3">
          <button class="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  @click="$emit('cancel')">Bekor qilish</button>
          <button class="rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-700"
                  @click="$emit('confirm')">O'chirish</button>
        </div>
      </div>
    </div>
    </transition>
  </Teleport>
</template>
