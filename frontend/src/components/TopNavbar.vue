<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from './AppIcon.vue'
import NavPopover from './NavPopover.vue'
import CalendarPanel from './CalendarPanel.vue'
import AiAssistantPanel from './AiAssistantPanel.vue'
import TasksPanel from './TasksPanel.vue'
import NotificationsPanel from './NotificationsPanel.vue'
import UserAvatar from './UserAvatar.vue'
import { db, auth, signOut, appearance, roleLabel, unreadCount } from '@/store'

defineProps({ title: String, subtitle: String })
defineEmits(['toggle-sidebar'])

const router = useRouter()

const glass = computed(() => appearance.mode === 'image' && !!appearance.image)

// Bir vaqtda faqat bitta panel ochiq turadi
const panel = ref(null)
const toggle = (name) => { panel.value = panel.value === name ? null : name }

const openTasks = computed(() =>
  db.tasks.filter((t) => !t.done && t.to === auth.user?.name).length
)
const unread = unreadCount

const userName = computed(() => auth.user?.name || '')
const userRole = roleLabel

function logOut() {
  panel.value = null
  signOut()
  router.push('/login')
}
</script>

<template>
  <!-- Fon rasmi rejimida backdrop-blur ISHLATILMAYDI:
       u header ostidagi wallpaper'ni blur qilib yuborardi. -->
  <header class="sticky top-0 z-30 border-b transition-colors"
          :class="glass
            ? 'border-white/40 bg-white/85'
            : 'border-slate-200 bg-white/90 backdrop-blur'">
    <div class="flex items-center gap-4 px-4 py-4 sm:px-6">
      <button class="text-slate-500 lg:hidden" aria-label="Menyuni ochish" @click="$emit('toggle-sidebar')">
        <AppIcon name="menu" class="h-6 w-6" />
      </button>

      <div class="min-w-0">
        <h1 class="truncate text-xl font-bold text-slate-900 sm:text-2xl">{{ title }}</h1>
        <p class="truncate text-xs text-slate-500 sm:text-sm">{{ subtitle }}</p>
      </div>

      <div class="ml-auto flex items-center gap-1 sm:gap-2">
        <!-- Kalendar -->
        <div class="relative">
          <button class="flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
                  :class="panel === 'calendar' ? 'bg-slate-100 text-slate-900' : ''"
                  @click="toggle('calendar')">
            <AppIcon name="calendar" class="h-5 w-5 text-slate-500" />
            <span class="hidden md:inline">Kalendar</span>
          </button>

          <NavPopover v-if="panel === 'calendar'" width="w-[340px]" @close="panel = null">
            <CalendarPanel />
          </NavPopover>
        </div>

        <!-- AI yordamchi -->
        <div class="relative">
          <button class="flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
                  :class="panel === 'ai' ? 'bg-slate-100 text-slate-900' : ''"
                  @click="toggle('ai')">
            <AppIcon name="bot" class="h-5 w-5 text-blue-500" />
            <span class="hidden md:inline">AI yordamchi</span>
          </button>

          <NavPopover v-if="panel === 'ai'" width="w-[420px]" @close="panel = null">
            <AiAssistantPanel />
          </NavPopover>
        </div>

        <!-- Vazifalar -->
        <div class="relative">
          <button class="relative flex items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
                  :class="panel === 'tasks' ? 'bg-slate-100 text-slate-900' : ''"
                  @click="toggle('tasks')">
            <AppIcon name="check-square" class="h-5 w-5 text-violet-500" />
            <span class="hidden md:inline">Vazifalar</span>
            <span v-if="openTasks"
                  class="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-violet-500 text-[10px] font-semibold text-white md:static md:h-5 md:w-5">
              {{ openTasks }}
            </span>
          </button>

          <NavPopover v-if="panel === 'tasks'" width="w-[400px]" @close="panel = null">
            <TasksPanel />
          </NavPopover>
        </div>

        <span class="hidden h-6 w-px bg-slate-200 md:block" />

        <!-- Bildirishnomalar -->
        <div class="relative">
          <button class="relative rounded-lg p-2 text-slate-500 transition hover:bg-slate-100"
                  :class="panel === 'notif' ? 'bg-slate-100 text-slate-900' : ''"
                  aria-label="Bildirishnomalar" @click="toggle('notif')">
            <AppIcon name="bell" class="h-5 w-5" />
            <span v-if="unread"
                  class="absolute -right-0.5 -top-0.5 grid h-5 w-5 place-items-center rounded-full bg-rose-500 text-[10px] font-semibold text-white">
              {{ unread }}
            </span>
          </button>

          <NavPopover v-if="panel === 'notif'" width="w-[380px]" @close="panel = null">
            <NotificationsPanel />
          </NavPopover>
        </div>

        <!-- Profil -->
        <div class="relative pl-1">
          <button class="flex items-center gap-2.5 rounded-xl p-1 pr-2 transition hover:bg-slate-100"
                  :class="panel === 'user' ? 'bg-slate-100' : ''"
                  aria-label="Profil menyusi" @click="toggle('user')">
            <UserAvatar :name="userName" size="md" />
            <span class="hidden leading-tight text-left sm:block">
              <span class="block text-sm font-semibold text-slate-900">{{ userName }}</span>
              <span class="block text-xs text-slate-500">{{ userRole }}</span>
            </span>
            <AppIcon name="chevron-down" class="hidden h-4 w-4 text-slate-400 transition sm:block"
                     :class="panel === 'user' ? 'rotate-180' : ''" />
          </button>

          <!-- Profil menyusi -->
          <NavPopover v-if="panel === 'user'" width="w-[280px]" @close="panel = null">
            <router-link to="/sozlamalar/profil"
                         class="flex items-center gap-3 px-4 py-3.5 transition hover:bg-slate-50"
                         @click="panel = null">
              <UserAvatar :name="userName" size="lg" />
              <span class="min-w-0 flex-1">
                <span class="block truncate text-sm font-semibold text-slate-900">{{ userName }}</span>
                <span class="block text-xs text-slate-500">Profilni ko'rish</span>
              </span>
              <AppIcon name="arrow-right" class="h-4 w-4 shrink-0 text-slate-300" />
            </router-link>

            <div class="mx-4 h-px bg-slate-100" />

            <nav class="py-1.5">
       
     
            </nav>

            <div class="mx-4 h-px bg-slate-100" />

            <div class="py-1.5">
              <button class="user-item w-full text-rose-600" @click="logOut">
                <AppIcon name="logout" class="h-[18px] w-[18px] text-rose-500" />
                Platformadan chiqish
              </button>
            </div>
          </NavPopover>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.user-item {
  @apply flex items-center gap-3 px-4 py-2.5 text-left text-sm font-medium text-slate-700 transition;
}
.user-item:hover { @apply bg-slate-50; }
</style>