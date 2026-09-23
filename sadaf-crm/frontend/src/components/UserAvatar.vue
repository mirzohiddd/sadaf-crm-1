<script setup>
import { computed } from 'vue'
import { initials, avatarTone } from '@/utils/format.js'

const props = defineProps({ name: String, size: { type: String, default: 'md' } })

const sizes = { sm: 'h-8 w-8 text-xs', md: 'h-10 w-10 text-sm', lg: 'h-12 w-12 text-base' }
const cls = computed(() => `${sizes[props.size]} ${avatarTone(props.name)}`)
</script>

<template>
  <span :class="cls" class="grid shrink-0 place-items-center rounded-full font-semibold">
    {{ initials(name) }}
  </span>
</template>
