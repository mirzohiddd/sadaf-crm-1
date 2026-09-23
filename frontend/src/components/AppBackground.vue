<script setup>
import { computed } from 'vue'
import { appearance } from '@/store'
const hasImage = computed(() => appearance.mode === 'image' && !!appearance.image)
const srcset = computed(() => appearance.imageSrcset || null)
const dim = computed(() => Math.max(0, Math.min(90, Number(appearance.dim) || 0)))
</script>
<template>
  <div class="app-bg" aria-hidden="true">
    <img
      v-if="hasImage"
      :src="appearance.image"
      :srcset="srcset"
      sizes="100vw"
      alt=""
      decoding="async"
      fetchpriority="high"
      class="app-bg__img"
    />
    <div v-else class="app-bg__solid" :style="{ background: appearance.color }" />
    <div v-if="hasImage && dim > 0" class="app-bg__overlay" :style="{ opacity: dim / 100 }" />
  </div>
</template>

<style scoped>
.app-bg {
  position: fixed;
  inset: 0;
  z-index: -10;
  overflow: hidden;
}

.app-bg__img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.app-bg__solid {
  width: 100%;
  height: 100%;
}
.app-bg__overlay {
  position: absolute;
  inset: 0;
  background: #ffffff;
  pointer-events: none;
}
</style>
