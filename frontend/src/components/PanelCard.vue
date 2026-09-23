<script setup>
defineProps({ title: String })
</script>

<template>
  <section class="card p-5">
    <header class="mb-4 flex items-center justify-between gap-3">
      <h2 class="text-base font-semibold text-slate-900">{{ title }}</h2>
      <slot name="action" />
    </header>
    <slot />
  </section>
</template>
