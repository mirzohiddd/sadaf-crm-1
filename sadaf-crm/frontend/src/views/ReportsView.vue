<script setup>
import { ref, reactive, onMounted } from 'vue'
import PanelCard from '@/components/PanelCard.vue'
import MetricTile from '@/components/MetricTile.vue'
import AppIcon from '@/components/AppIcon.vue'
import { reportsApi } from '@/api'
import { money } from '@/utils/format.js'

// Hisobotlar backendda tayyorlanadi:
//  • Excel — openpyxl orqali .xlsx fayl (GET /api/reports/excel)

const loading = ref(true)
const reports = ref([])
const totals = ref({})

const busy = reactive({})          // { [kind]: 'excel' }
const message = reactive({ text: '', ok: false, link: '' })

const ICONS = {
  leads: 'send', clients: 'users', tours: 'bag', sales: 'dollar',
  employees: 'user', tasks: 'check-square', attendance: 'clock'
}

const TONES = {
  leads: 'bg-sky-50 text-sky-600', clients: 'bg-emerald-50 text-emerald-600',
  tours: 'bg-amber-50 text-amber-600', sales: 'bg-violet-50 text-violet-600',
  employees: 'bg-blue-50 text-blue-600', tasks: 'bg-rose-50 text-rose-600',
  attendance: 'bg-teal-50 text-teal-600'
}

function say(text, ok = false, link = '') {
  Object.assign(message, { text, ok, link })
  setTimeout(() => { message.text = '' }, 6000)
}

async function load() {
  loading.value = true
  try {
    const data = await reportsApi.list()
    reports.value = data.reports
    totals.value = data.totals || {}
  } catch (err) {
    say(err?.message || "Hisobotlarni yuklab bo'lmadi.")
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function toExcel(kind) {
  if (busy[kind]) return
  busy[kind] = 'excel'
  try {
    await reportsApi.exportExcel(kind)
    say('Excel fayl yuklandi.', true)
  } catch (err) {
    say(err?.message || "Excel faylni yaratib bo'lmadi.")
  } finally {
    busy[kind] = null
  }
}

</script>

<template>
  <div class="space-y-5">
    <!-- Umumiy ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile label="Jami leadlar" :value="totals.leads ?? 0" unit="ta" icon="send" color="blue" />
      <MetricTile label="Mijozlar" :value="totals.clients ?? 0" unit="ta" icon="users" color="violet" />
      <MetricTile label="Yopilgan summa" :value="money(totals.revenue)" icon="dollar" color="green" />
      <MetricTile label="Konversiya" :value="totals.conversion || '0%'" icon="chart" color="amber" />
    </div>

    <!-- Holat xabari -->
    <p v-if="message.text" class="flex flex-wrap items-center gap-2 rounded-xl px-4 py-3 text-sm"
       :class="message.ok ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">
      <AppIcon :name="message.ok ? 'check-circle' : 'x-circle'" class="h-4 w-4 shrink-0" />
      {{ message.text }}
      <a v-if="message.link" :href="message.link" target="_blank" rel="noopener"
         class="font-semibold underline">Hujjatni ochish</a>
    </p>

    <!-- Barchasini yuklab olish -->
    <PanelCard title="To'liq hisobot">
      <div class="flex flex-wrap items-center gap-4">
        <p class="min-w-[220px] flex-1 text-sm text-slate-500">
          Barcha bo'limlar bitta Excel faylga yig'iladi — har biri alohida varaqda.
        </p>
        <button class="btn-accent flex items-center gap-2 disabled:opacity-60"
                :disabled="busy.all" @click="toExcel('all')">
          <AppIcon :name="busy.all ? 'refresh' : 'download'" class="h-4 w-4"
                   :class="busy.all && 'animate-spin'" />
          {{ busy.all ? 'Tayyorlanmoqda...' : 'Hammasini Excel (.xlsx)' }}
        </button>
      </div>
    </PanelCard>

    <!-- Bo'limlar -->
    <p v-if="loading" class="card p-12 text-center text-sm text-slate-500">Yuklanmoqda...</p>

    <div v-else class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <article v-for="r in reports" :key="r.key" class="card flex flex-col p-5">
        <span class="grid h-11 w-11 place-items-center rounded-xl" :class="TONES[r.key] || 'bg-slate-50 text-slate-600'">
          <AppIcon :name="ICONS[r.key] || 'bars'" class="h-5 w-5" />
        </span>

        <h2 class="mt-4 text-base font-semibold text-slate-900">{{ r.title }}</h2>
        <p class="mt-1 text-sm text-slate-500">
          {{ r.count }} ta yozuv · {{ r.period }}
        </p>

        <div class="mt-5 flex flex-1 flex-col justify-end gap-2">
          <button class="flex items-center justify-center gap-2 rounded-xl border border-slate-200 py-2.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
                  :disabled="!r.ready || busy[r.key]" @click="toExcel(r.key)">
            <AppIcon :name="busy[r.key] === 'excel' ? 'refresh' : 'download'" class="h-4 w-4"
                     :class="busy[r.key] === 'excel' && 'animate-spin'" />
            Excel
          </button>

          <p v-if="!r.ready" class="text-center text-xs text-slate-400">
            Ma'lumot to'plangach faollashadi
          </p>
        </div>
      </article>
    </div>
  </div>
</template>
