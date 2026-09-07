<script setup>
import { ref, computed, watch, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import TopNavbar from '@/components/TopNavbar.vue'
import AppBackground from '@/components/AppBackground.vue'
import AppIcon from '@/components/AppIcon.vue'
import { ui, notificationsApi } from '@/store'

const route = useRoute()
const sidebarOpen = ref(false)

// Sidebar yig'ilgan holati — layout darajasida saqlanadi,
// shuning uchun navbar va kontent kengligi ham to'g'ri o'zgaradi.
const collapsed = ref(localStorage.getItem('sadaf_sidebar') === '1')

function toggleCollapse() {
  collapsed.value = !collapsed.value
  localStorage.setItem('sadaf_sidebar', collapsed.value ? '1' : '0')
}

// Sahifa almashsa mobil sidebar avtomatik yopiladi
watch(() => route.path, () => { sidebarOpen.value = false })

const title = computed(() => route.meta.title || 'Dashboard')
const subtitle = computed(() => route.meta.subtitle || '')

// Bildirishnomalarni har 60 soniyada yangilaymiz —
// hamkasb vazifa bersa navbardagi hisoblagich o'zi o'zgaradi.
const timer = setInterval(() => notificationsApi.reload(), 60_000)
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <!-- overflow-x-hidden: sahifa animatsiyasi (translateX) gorizontal scroll hosil
       qilib, fixed sidebar "sakrab" ketishiga sabab bo'lardi. -->
  <div class="relative min-h-screen overflow-x-hidden">
    <AppBackground />

    <SidebarNav
      :open="sidebarOpen"
      :collapsed="collapsed"
      @close="sidebarOpen = false"
      @toggle-collapse="toggleCollapse"
    />

    <!-- Kontent: sidebar kengligiga qarab suriladi -->
    <div class="min-w-0 transition-[padding] duration-200"
         :class="collapsed ? 'lg:pl-[68px]' : 'lg:pl-[236px]'">
      <TopNavbar :title="title" :subtitle="subtitle" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <!-- Global xatolik xabari (API bilan bog'liq muammolar) -->
      <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0 -translate-y-2"
                  leave-active-class="transition duration-150" leave-to-class="opacity-0">
        <div v-if="ui.error"
             class="mx-4 mt-4 flex items-start gap-2 rounded-xl bg-rose-50 px-4 py-3 text-sm text-rose-700 sm:mx-6">
          <AppIcon name="x-circle" class="mt-0.5 h-4 w-4 shrink-0" />
          <span class="flex-1">{{ ui.error }}</span>
          <button class="shrink-0 rounded-md p-0.5 hover:bg-rose-100" aria-label="Yopish"
                  @click="ui.error = ''">
            <AppIcon name="close" class="h-4 w-4" />
          </button>
        </div>
      </Transition>

      <main class="min-w-0 overflow-x-hidden p-4 sm:p-6">
        <router-view v-slot="{ Component, route: r }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="r.path" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>
