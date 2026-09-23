<script setup>
import { computed } from 'vue'
const props = defineProps({
  size: { type: String, default: 'h-11' },
  variant: { type: String, default: 'light' } 
})
const src = computed(() => (props.variant === 'dark' ? '/logo-dark.png' : '/logo.png'))
</script>
<template>
  <img :src="src" alt="SADAF travel agency" class="w-auto object-contain" :class="size" />
</template>
