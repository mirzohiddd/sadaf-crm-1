<script setup>
import AppIcon from '@/components/AppIcon.vue'

const sections = [
  { to: '/sozlamalar/profil', label: 'Profil',         icon: 'user' },
  { to: '/sozlamalar/fon',    label: 'Orqa fon',       icon: 'image' },
  // { to: '/sozlamalar/parol',  label: 'Login va parol', icon: 'lock' }
]
</script>

<template>
  <div class="flex flex-col gap-5 lg:flex-row lg:items-start">
    <aside class="animate-slide-left w-full shrink-0 rounded-2xl border border-slate-200 bg-white p-3 lg:sticky lg:top-24 lg:w-[220px]">
      <nav class="flex gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
        <router-link
          v-for="s in sections" :key="s.to" :to="s.to"
          class="tab-link"
        >
          <AppIcon :name="s.icon" class="h-4 w-4" />
          {{ s.label }}
        </router-link>
      </nav>
    </aside>
    <div class="min-w-0 flex-1">
      <router-view v-slot="{ Component, route: r }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="r.path" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>
.tab-link {
  @apply flex shrink-0 items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-slate-600 transition;
}
.tab-link:hover {
  @apply bg-slate-50;
}
.tab-link :deep(svg) { color: #94a3b8; }
.tab-link.router-link-active {
  background: var(--accent-soft);
  color: var(--accent);
}
.tab-link.router-link-active :deep(svg) { color: var(--accent); }
</style>
