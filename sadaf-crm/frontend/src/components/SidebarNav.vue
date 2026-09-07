<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import BrandLogo from './BrandLogo.vue'
import { appearance, canSee, leadBadge } from '@/store'

defineProps({ open: Boolean, collapsed: Boolean })
defineEmits(['close', 'toggle-collapse'])

// Fon rasmi tanlansa — sidebar shaffof bo'ladi va rasm ostidan ko'rinadi
const glass = computed(() => appearance.mode === 'image' && !!appearance.image)

// `page` kaliti backenddagi ROLE_PAGES bilan bir xil.
// Rolga yopiq bo'lim navbarda umuman ko'rinmaydi (backend ham tekshiradi).
const ALL_LINKS = [
  { to: '/dashboard', page: 'dashboard', label: 'Dashboard', icon: 'home'  },
  { to: '/hodimlar',  page: 'hodimlar',  label: 'Hodimlar',  icon: 'user'  },
  { to: '/turlar',    page: 'turlar',    label: 'Turlar',    icon: 'bag'   },
  { to: '/ledlar',    page: 'ledlar',    label: 'Ledlar',    icon: 'send'  },
  { to: '/mijozlar',  page: 'mijozlar',  label: 'Mijozlar',  icon: 'users' },
  // { to: '/savdolar',  page: 'savdolar',  label: 'Savdolar',  icon: 'dollar' },
  { to: '/analitika', page: 'analitika', label: 'Analitika', icon: 'pie'   },
  { to: '/hisobot',   page: 'hisobot',   label: 'Hisobot',   icon: 'bars'  }
]

const links = computed(() =>
  ALL_LINKS.filter((l) => canSee(l.page)).map((l) => ({
    ...l,
    // Ledlar yonida hali ko'rilmagan (yangi) leadlar soni ko'rsatiladi —
    // har bir admin/hodim uchun alohida, Super Admin uchun barchasi
    badge: l.page === 'ledlar' ? (leadBadge.count || null) : null
  }))
)
</script>

<template>
  <!-- Mobil overlay -->
  <div v-if="open" class="fixed inset-0 z-30 bg-slate-900/50 lg:hidden" @click="$emit('close')" />

  <aside
    class="fixed inset-y-0 left-0 z-40 flex h-screen flex-col overflow-hidden transition-[width,transform] duration-200 lg:translate-x-0"
    :class="[
      open ? 'translate-x-0' : '-translate-x-full',
      collapsed ? 'w-[68px]' : 'w-[236px]',
      glass ? 'bg-navy-900/90' : 'bg-navy-900'
    ]"
  >
    <!-- Yuqori: logotip = ochish/yopish tugmasi -->
    <div class="pb-3 pt-4" :class="collapsed ? 'px-2' : 'px-3'">
      <div class="flex items-center gap-2">
        <!-- Logotipni bosish sidebarni ochadi/yopadi -->
        <button
          class="group flex min-w-0 flex-1 items-center justify-center rounded-xl p-1.5 transition hover:bg-white/10"
          :aria-label="collapsed ? 'Menyuni ochish' : 'Menyuni yigish'"
          :title="collapsed ? 'Menyuni ochish' : 'Menyuni yigish'"
          :aria-expanded="!collapsed"
          @click="$emit('toggle-collapse')"
        >
          <BrandLogo v-if="!collapsed" size="h-16" variant="light"
                     class="mx-auto transition group-hover:scale-[1.03]" />
          <img v-else src="/favicon.png" alt="SADAF"
               class="h-9 w-9 rounded-lg object-contain transition group-hover:scale-110" />
        </button>

        <!-- Mobilda yopish tugmasi -->
        <button v-if="!collapsed" class="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-white/10 hover:text-white lg:hidden"
                aria-label="Yopish" @click="$emit('close')">
          <AppIcon name="close" class="h-5 w-5" />
        </button>
      </div>
    </div>

    <div class="mx-3 h-px bg-white/10" />

    <!-- Menyu -->
    <nav class="flex-1 overflow-y-auto overflow-x-hidden overscroll-contain py-3" :class="collapsed ? 'px-2' : 'px-3'">
      <ul class="space-y-1">
        <li v-for="l in links" :key="l.to">
          <router-link
            :to="l.to"
            class="side-link group relative"
            :class="collapsed && 'h-11 w-11 justify-center px-0'"
            @click="$emit('close')"
          >
            <span class="relative shrink-0">
              <AppIcon :name="l.icon" class="h-5 w-5" />
              <span v-if="l.badge"
                    class="absolute -right-2 -top-2 flex min-w-[18px] items-center justify-center rounded-full px-1 text-[10px] font-bold leading-[16px] text-white ring-2 ring-navy-900"
                    style="background: var(--accent)">
                {{ l.badge }}
              </span>
            </span>

            <span v-if="!collapsed" class="truncate">{{ l.label }}</span>

            <span v-if="collapsed"
                  class="pointer-events-none absolute left-full z-50 ml-2 hidden whitespace-nowrap rounded-lg bg-navy-800 px-2.5 py-1.5 text-xs text-white shadow-lg group-hover:block">
              {{ l.label }}
            </span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- Pastki: Sozlamalar -->
    <div class="border-t border-white/10 py-3" :class="collapsed ? 'px-2' : 'px-3'">
      <router-link
        to="/sozlamalar"
        class="side-link group relative"
        :class="collapsed && 'h-11 w-11 justify-center px-0'"
        @click="$emit('close')"
      >
        <AppIcon name="gear" class="h-5 w-5 shrink-0" />
        <span v-if="!collapsed">Sozlamalar</span>
        <span v-if="collapsed"
              class="pointer-events-none absolute left-full z-50 ml-2 hidden whitespace-nowrap rounded-lg bg-navy-800 px-2.5 py-1.5 text-xs text-white shadow-lg group-hover:block">
          Sozlamalar
        </span>
      </router-link>
    </div>
  </aside>
</template>

<style scoped>
.side-link {
  @apply flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-300 transition;
}
.side-link:hover {
  @apply bg-white/[.07] text-white;
}
.side-link.router-link-active {
  @apply bg-white/[.12] text-white;
  box-shadow: inset 0 0 0 1px var(--accent-ring);
}
.side-link.router-link-active :deep(svg) {
  color: var(--accent);
}
</style>