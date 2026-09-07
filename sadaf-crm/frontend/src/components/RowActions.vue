<script setup>
import AppIcon from './AppIcon.vue'

defineProps({ view: Boolean })
defineEmits(['view', 'edit', 'remove'])
</script>

<template>
  <div class="flex items-center justify-end gap-2">
    <button v-if="view" class="grid h-9 w-9 place-items-center rounded-lg bg-slate-50 text-slate-500 hover:bg-slate-100"
            title="Ko'rish" @click="$emit('view')">
      <AppIcon name="eye" class="h-4 w-4" />
    </button>
    <button class="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100"
            title="Tahrirlash" @click="$emit('edit')">
      <AppIcon name="pencil" class="h-4 w-4" />
    </button>
    <button class="grid h-9 w-9 place-items-center rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100"
            title="O'chirish" @click="$emit('remove')">
      <AppIcon name="trash" class="h-4 w-4" />
    </button>
  </div>
</template>
