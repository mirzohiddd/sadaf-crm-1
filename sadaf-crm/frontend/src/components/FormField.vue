<script setup>
defineProps({
  label: String,
  required: Boolean,
  error: String,
  hint: String
})
</script>
<template>
  <div>
    <label class="mb-1.5 block text-sm font-medium text-slate-700">
      {{ label }} <span v-if="required" class="text-rose-500">*</span>
    </label>
    <slot />
    <p v-if="error" class="mt-1 text-xs text-rose-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-xs text-slate-400">{{ hint }}</p>
  </div>
</template>
