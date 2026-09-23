<script setup>
import logoSrc from '../assets/logo.png'

defineProps({
  variant: {
    type: String,
    default: 'full', // 'full' shows the full lockup image, 'mark' crops tighter for small spaces
    validator: (v) => ['full', 'mark'].includes(v)
  }
})
</script>

<template>
  <img
    :src="logoSrc"
    alt="SADAF travel agency"
    class="h-14 w-auto select-none object-contain drop-shadow-[0_2px_10px_rgba(15,17,40,0.55)] sm:h-16 lg:h-[4.5rem]"
    :class="variant === 'mark' ? 'max-w-[44px] object-left' : ''"
    draggable="false"
  />
</template>