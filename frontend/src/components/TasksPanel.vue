<script setup>
import { ref, computed, reactive } from 'vue'
import AppIcon from './AppIcon.vue'
import { db, tasksApi, auth } from '@/store'
import { todayUz } from '@/utils/format.js'

const tab = ref('menga') // menga | mendan | hammasi
const adding = ref(false)
const error = ref('')

const me = computed(() => auth.user?.name || '')

const form = reactive({ title: '', to: '', due: todayUz(), time: '09:00', priority: "O'rta" })

// Vazifa biriktirish ro'yxati backenddan keladi (/api/employees/directory).
// Unda faqat ism va lavozim bor — login/parol yo'q, shuning uchun
// operator ham hamkasbiga vazifa bera oladi.
const colleagues = computed(() =>
  (db.directory.length ? db.directory : db.employees).filter((e) => e.name !== me.value)
)

const lists = computed(() => ({
  menga: db.tasks.filter((t) => t.to === me.value),
  mendan: db.tasks.filter((t) => t.from === me.value),
  hammasi: db.tasks
}))

const shown = computed(() =>
  [...lists.value[tab.value]].sort((a, b) => Number(a.done) - Number(b.done))
)

const tabs = [
  { key: 'menga', label: 'Menga' },
  { key: 'mendan', label: 'Men berdim' },
  { key: 'hammasi', label: 'Hammasi' }
]

const priorityTone = {
  Yuqori: 'bg-rose-50 text-rose-700',
  "O'rta": 'bg-amber-50 text-amber-700',
  Past: 'bg-slate-100 text-slate-600'
}

async function submit() {
  if (!form.title.trim()) {
    error.value = 'Vazifa matnini kiriting.'
    return
  }
  if (!form.to) {
    error.value = 'Kimga berilishini tanlang.'
    return
  }
  error.value = ''
  const row = await tasksApi.add({ ...form, done: false })
  if (!row) {
    error.value = "Vazifani saqlab bo'lmadi. Qaytadan urinib ko'ring."
    return
  }
  Object.assign(form, { title: '', to: '', due: todayUz(), time: '09:00', priority: "O'rta" })
  adding.value = false
  tab.value = 'mendan'
}
</script>

<template>
  <div>
    <!-- Sarlavha va tablar -->
    <div class="border-b border-slate-100 px-4 py-3">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-semibold text-slate-900">Vazifalar</h2>
        <button class="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-blue-700"
                @click="adding = !adding">
          <AppIcon :name="adding ? 'close' : 'plus'" class="h-3.5 w-3.5" />
          {{ adding ? 'Yopish' : 'Vazifa berish' }}
        </button>
      </div>

      <div class="mt-3 flex gap-1 rounded-xl bg-slate-100 p-1">
        <button v-for="t in tabs" :key="t.key"
                class="flex-1 rounded-lg py-1.5 text-xs font-medium transition"
                :class="tab === t.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                @click="tab = t.key">
          {{ t.label }}
          <span class="ml-1 text-slate-400">{{ lists[t.key].length }}</span>
        </button>
      </div>
    </div>

    <!-- Yangi vazifa formasi -->
    <div v-if="adding" class="animate-fade-up space-y-2.5 border-b border-slate-100 bg-slate-50/70 px-4 py-3">
      <input v-model="form.title" class="field bg-white py-2 text-sm" placeholder="Vazifa matni"
             @keyup.enter="submit" />

      <select v-model="form.to" class="field bg-white py-2 text-sm">
        <option value="" disabled>Kimga berilsin?</option>
        <option v-for="e in colleagues" :key="e.id" :value="e.name">
          {{ e.name }}{{ e.position ? ' — ' + e.position : '' }}
        </option>
      </select>

      <div class="grid grid-cols-3 gap-2">
        <input v-model="form.due" class="field bg-white py-2 text-sm" placeholder="DD.MM.YYYY" />
        <input v-model="form.time" type="time" class="field bg-white py-2 text-sm" />
        <select v-model="form.priority" class="field bg-white py-2 text-sm">
          <option>Yuqori</option>
          <option>O'rta</option>
          <option>Past</option>
        </select>
      </div>

      <p v-if="error" class="text-xs text-rose-600">{{ error }}</p>

      <button class="w-full rounded-xl bg-blue-600 py-2 text-sm font-semibold text-white hover:bg-blue-700"
              @click="submit">Saqlash</button>
    </div>

    <!-- Ro'yxat -->
    <ul v-if="shown.length" class="max-h-[320px] divide-y divide-slate-50 overflow-y-auto">
      <li v-for="t in shown" :key="t.id" class="flex items-start gap-3 px-4 py-3 hover:bg-slate-50">
        <button class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-md border-2 transition"
                :class="t.done ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300 hover:border-blue-400'"
                :aria-label="t.done ? 'Bajarilmagan deb belgilash' : 'Bajarildi deb belgilash'"
                @click="tasksApi.toggle(t.id)">
          <AppIcon v-if="t.done" name="check-circle" class="h-3.5 w-3.5" />
        </button>

        <span class="min-w-0 flex-1">
          <span class="block text-sm" :class="t.done ? 'text-slate-400 line-through' : 'text-slate-800'">
            {{ t.title }}
          </span>
          <span class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-400">
            <span class="badge" :class="priorityTone[t.priority]">{{ t.priority }}</span>
            <span>{{ t.from }} → {{ t.to }}</span>
            <span>{{ t.due }} {{ t.time }}</span>
          </span>
        </span>

        <button class="shrink-0 rounded-md p-1 text-slate-300 hover:bg-slate-100 hover:text-rose-500"
                aria-label="O'chirish" @click="tasksApi.remove(t.id)">
          <AppIcon name="trash" class="h-3.5 w-3.5" />
        </button>
      </li>
    </ul>

    <p v-else class="px-4 py-10 text-center text-sm text-slate-400">
      Bu bo'limda vazifa yo'q.
    </p>
  </div>
</template>
