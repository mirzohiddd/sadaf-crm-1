<script setup>
import { ref, computed, reactive } from 'vue'
import PanelCard from '@/components/PanelCard.vue'
import MetricTile from '@/components/MetricTile.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import FormField from '@/components/FormField.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import SourceTag from '@/components/SourceTag.vue'
import AppIcon from '@/components/AppIcon.vue'
import AreaChart from '@/components/AreaChart.vue'
import DonutChart from '@/components/DonutChart.vue'
import BarChart from '@/components/BarChart.vue'
import { db, auth, activityText, isAdmin as storeIsAdmin, roleLabel, loadActivity } from '@/store'
import { authApi } from '@/api'
import { onMounted } from 'vue'
import { money, initials } from '@/utils/format.js'

const me = computed(() => auth.user?.name || '')
const isAdmin = storeIsAdmin

onMounted(loadActivity)

// Hodimlar ro'yxatidan o'zim haqimdagi yozuv
const myRecord = computed(() => db.employees.find((e) => e.name === me.value) || null)

const profile = reactive({
  name: auth.user?.name || '',
  email: auth.user?.email || '',
  phone: auth.user?.phone || ''
})

const editOpen = ref(false)
const draft = reactive({ ...profile })

function openEdit() {
  Object.assign(draft, profile)
  editOpen.value = true
}
const saveError = ref('')

async function saveProfile() {
  saveError.value = ''
  try {
    // Profil backendda yangilanadi; ism o'zgarsa CRM yozuvlaridagi
    // "mas'ul" bog'lanishlari ham avtomatik ko'chadi.
    const updated = await authApi.updateProfile({ ...draft })
    Object.assign(profile, { name: updated.name, email: updated.email, phone: updated.phone })
    auth.user = updated
    localStorage.setItem('sadaf_user', JSON.stringify(updated))
    editOpen.value = false
  } catch (err) {
    saveError.value = err?.message || "Profilni saqlab bo'lmadi."
  }
}

// ——— Davr filtri ———

const RANGES = [
  { key: 7, label: 'Haftalik' },
  { key: 30, label: 'Oylik' },
  { key: 365, label: 'Yillik' }
]
const range = ref(7)

// "18.05.2025" -> Date
function parseUz(d) {
  const m = /^(\d{2})\.(\d{2})\.(\d{4})$/.exec(String(d || ''))
  return m ? new Date(+m[3], +m[2] - 1, +m[1]) : null
}
const daysAgo = (n) => {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() - n)
  return d
}
const inRange = (d) => {
  const t = parseUz(d)
  return t ? t >= daysAgo(range.value - 1) : false
}

// ——— Mening ma'lumotlarim ———
// Admin butun tizimni, menejer esa faqat o'ziga biriktirilganni ko'radi.

const mine = (list, field = 'manager') =>
  isAdmin.value ? list : list.filter((x) => x[field] === me.value)

const myLeads = computed(() => mine(db.leads))
const myClients = computed(() => (isAdmin.value ? db.clients : db.clients.filter((c) => c.manager === me.value)))

const WON = ['Bron tasdiqlandi', "To'lov qilindi"]
const LOST = ['Bekor qilindi', 'Sifatsiz lead']

const periodLeads = computed(() => myLeads.value.filter((l) => inRange(l.date)))
const wonLeads = computed(() => periodLeads.value.filter((l) => WON.includes(l.stage)))

const stats = computed(() => {
  const total = periodLeads.value.length
  const won = wonLeads.value.length
  const revenue = wonLeads.value.reduce((s, l) => s + Number(l.amount || 0), 0)
  const lost = periodLeads.value.filter((l) => LOST.includes(l.stage)).length
  return {
    total,
    won,
    lost,
    revenue,
    conversion: total ? Math.round((won / total) * 100) : 0,
    avgCheck: won ? Math.round(revenue / won) : 0,
    pipeline: periodLeads.value
      .filter((l) => !WON.includes(l.stage) && !LOST.includes(l.stage))
      .reduce((s, l) => s + Number(l.amount || 0), 0)
  }
})

// ——— Kunlik dinamika (grafik) ———

const dayKeys = computed(() => {
  const n = range.value === 7 ? 7 : range.value === 30 ? 30 : 12
  const out = []
  if (range.value === 365) {
    const now = new Date()
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
      out.push({ key: `${d.getFullYear()}-${d.getMonth()}`, label: d.toLocaleDateString('ru-RU', { month: 'short' }) })
    }
    return out
  }
  for (let i = n - 1; i >= 0; i--) {
    const d = daysAgo(i)
    out.push({
      key: `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`,
      label: `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}`
    })
  }
  return out
})

const chart = computed(() => {
  const buckets = new Map(dayKeys.value.map((d) => [d.key, 0]))
  wonLeads.value.forEach((l) => {
    const d = parseUz(l.date)
    if (!d) return
    const key = range.value === 365
      ? `${d.getFullYear()}-${d.getMonth()}`
      : `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
    if (buckets.has(key)) buckets.set(key, buckets.get(key) + Number(l.amount || 0))
  })
  return {
    points: [...buckets.values()],
    labels: dayKeys.value.map((d) => d.label)
  }
})

// ——— Manbalar taqsimoti ———

const SOURCE_COLORS = {
  Telegram: '#38bdf8', Instagram: '#f43f5e', Sayt: '#8b5cf6', "Qo'ng'iroq": '#f59e0b'
}

const bySource = computed(() => {
  const map = new Map()
  periodLeads.value.forEach((l) => map.set(l.source, (map.get(l.source) || 0) + 1))
  return [...map.entries()]
    .map(([label, value]) => ({ label, value, color: SOURCE_COLORS[label] || '#94a3b8' }))
    .sort((a, b) => b.value - a.value)
})

// ——— Turlar bo'yicha ———

const byTour = computed(() => {
  const map = new Map()
  wonLeads.value.forEach((l) => map.set(l.tour, (map.get(l.tour) || 0) + 1))
  return [...map.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6)
})

// ——— Faoliyat jurnali ———

const myActivity = computed(() =>
  (isAdmin.value ? db.activity : db.activity.filter((a) => a.actor === me.value)).slice(0, 40)
)

const ACTION_TONE = {
  create: { dot: 'bg-emerald-500', icon: 'plus' },
  update: { dot: 'bg-blue-500', icon: 'pencil' },
  delete: { dot: 'bg-rose-500', icon: 'trash' },
  stage: { dot: 'bg-violet-500', icon: 'arrow-right' },
  done: { dot: 'bg-teal-500', icon: 'check-circle' }
}

function whenText(ts) {
  const d = new Date(ts)
  const diff = (Date.now() - d) / 60000
  if (diff < 1) return 'Hozir'
  if (diff < 60) return `${Math.floor(diff)} daqiqa oldin`
  if (diff < 24 * 60) return `${Math.floor(diff / 60)} soat oldin`
  return d.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Bugungi faoliyat soni
const todayActions = computed(() => {
  const start = daysAgo(0)
  return myActivity.value.filter((a) => new Date(a.ts) >= start).length
})

// ——— Tablar ———

const tabs = [
  { key: 'stats', label: 'Statistika' },
  { key: 'deals', label: 'Savdolarim' },
  { key: 'clients', label: 'Mijozlarim' },
  { key: 'activity', label: 'Faoliyatim' }
]
const tab = ref('stats')

const myTasks = computed(() => db.tasks.filter((t) => t.to === me.value))
const openTasks = computed(() => myTasks.value.filter((t) => !t.done).length)
</script>

<template>
  <div class="space-y-5">
    <!-- ——— Profil kartochkasi ——— -->
    <section class="card p-5">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-center">
        <div class="flex items-center gap-4">
          <span class="relative grid h-16 w-16 shrink-0 place-items-center rounded-2xl bg-blue-100 text-xl font-bold text-blue-700">
            {{ initials(profile.name) }}
            <span class="absolute -bottom-0.5 -right-0.5 h-4 w-4 rounded-full border-2 border-white bg-emerald-500" />
          </span>
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="truncate text-lg font-bold text-slate-900">{{ profile.name }}</h2>
              <StatusBadge :status="roleLabel" />
            </div>
            <p class="mt-1 text-sm text-slate-500">{{ profile.email }}</p>
            <p class="flex items-center gap-1.5 text-sm text-slate-500">
              <AppIcon name="phone" class="h-3.5 w-3.5 text-emerald-500" /> {{ profile.phone }}
            </p>
          </div>
        </div>

        <dl class="grid flex-1 grid-cols-2 gap-4 border-slate-100 sm:grid-cols-3 lg:border-l lg:pl-6">
          <div>
            <dt class="text-xs text-slate-400">Lavozim</dt>
            <dd class="text-sm font-medium text-slate-800">{{ auth.user?.position || myRecord?.position || '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">CRM roli</dt>
            <dd class="text-sm font-medium text-slate-800">{{ roleLabel }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Ishga kirgan sana</dt>
            <dd class="text-sm font-medium text-slate-800">{{ auth.user?.hireDate || myRecord?.hireDate || '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Bugungi amallar</dt>
            <dd class="text-sm font-medium text-slate-800">{{ todayActions }} ta</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Ochiq vazifalar</dt>
            <dd class="text-sm font-medium text-slate-800">{{ openTasks }} ta</dd>
          </div>
          <div>
            <dt class="text-xs text-slate-400">Ish vaqti</dt>
            <dd class="text-sm font-medium text-slate-800">{{ auth.user?.shift || myRecord?.shift || '—' }}</dd>
          </div>
        </dl>

        <button class="flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 lg:self-start"
                @click="openEdit">
          <AppIcon name="pencil" class="h-4 w-4" /> Profilni tahrirlash
        </button>
      </div>
    </section>

    <!-- ——— Tablar + davr ——— -->
    <div class="card flex flex-wrap items-center gap-3 p-3">
      <nav class="flex flex-1 gap-1 overflow-x-auto">
        <button v-for="t in tabs" :key="t.key"
                class="shrink-0 rounded-lg px-3.5 py-2 text-sm font-medium transition"
                :class="tab === t.key ? 'bg-blue-50 text-blue-700' : 'text-slate-500 hover:bg-slate-50'"
                @click="tab = t.key">
          {{ t.label }}
        </button>
      </nav>

      <div v-if="tab !== 'activity'" class="flex gap-1 rounded-xl bg-slate-100 p-1">
        <button v-for="r in RANGES" :key="r.key"
                class="rounded-lg px-3 py-1.5 text-xs font-medium transition"
                :class="range === r.key ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
                @click="range = r.key">
          {{ r.label }}
        </button>
      </div>
    </div>

    <!-- ——— STATISTIKA ——— -->
    <template v-if="tab === 'stats'">
      <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricTile label="Yopilgan savdo" :value="money(stats.revenue)" icon="dollar" color="green"
                    :note="`${stats.won} ta bitim`" />
        <MetricTile label="Kelgan leadlar" :value="stats.total" unit="ta" icon="users" color="blue"
                    :note="`${stats.lost} ta yo'qotilgan`" />
        <MetricTile label="Konversiya" :value="stats.conversion + '%'" icon="chart" color="violet"
                    note="Yopilgan / kelgan" />
        <MetricTile label="O'rtacha chek" :value="money(stats.avgCheck)" icon="handshake" color="amber"
                    :note="`Voronkada ${money(stats.pipeline)}`" />
      </div>

      <div class="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <PanelCard title="Savdo dinamikasi" class="xl:col-span-2">
          <AreaChart :points="chart.points" :labels="chart.labels" />
        </PanelCard>

        <PanelCard title="Leadlar manbasi">
          <DonutChart :data="bySource" center-label="Leadlar" />
        </PanelCard>
      </div>

      <PanelCard title="Eng ko'p sotilgan turlar">
        <BarChart :data="byTour" />
      </PanelCard>
    </template>

    <!-- ——— SAVDOLARIM ——— -->
    <PanelCard v-else-if="tab === 'deals'" title="Yopilgan bitimlar">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[720px] text-sm">
          <thead>
            <tr class="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="py-3 pr-4 font-medium">Mijoz</th>
              <th class="py-3 pr-4 font-medium">Tur</th>
              <th class="py-3 pr-4 font-medium">Manba</th>
              <th class="py-3 pr-4 font-medium">Sana</th>
              <th class="py-3 pr-4 font-medium">Bosqich</th>
              <th class="py-3 text-right font-medium">Summa</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in wonLeads" :key="l.id" class="border-b border-slate-50 last:border-0">
              <td class="py-3 pr-4 font-medium text-slate-900">{{ l.name }}</td>
              <td class="py-3 pr-4 text-slate-600">{{ l.tour }} · {{ l.people }} kishi</td>
              <td class="py-3 pr-4"><SourceTag :source="l.source" /></td>
              <td class="py-3 pr-4 text-slate-600">{{ l.date }}</td>
              <td class="py-3 pr-4"><StatusBadge :status="l.stage" /></td>
              <td class="py-3 text-right font-semibold text-slate-900">{{ money(l.amount) }}</td>
            </tr>
            <tr v-if="!wonLeads.length">
              <td colspan="6" class="py-12 text-center text-sm text-slate-500">
                Bu davrda yopilgan bitim yo'q.
              </td>
            </tr>
          </tbody>
          <tfoot v-if="wonLeads.length">
            <tr class="border-t border-slate-100">
              <td colspan="5" class="py-3 text-sm font-medium text-slate-500">Jami</td>
              <td class="py-3 text-right text-base font-bold text-slate-900">{{ money(stats.revenue) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </PanelCard>

    <!-- ——— MIJOZLARIM ——— -->
    <PanelCard v-else-if="tab === 'clients'" :title="`Mijozlar (${myClients.length} ta)`">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[720px] text-sm">
          <thead>
            <tr class="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="py-3 pr-4 font-medium">Mijoz</th>
              <th class="py-3 pr-4 font-medium">Telefon</th>
              <th class="py-3 pr-4 font-medium">Oxirgi tur</th>
              <th class="py-3 pr-4 font-medium">Safarlar</th>
              <th class="py-3 pr-4 font-medium">Holat</th>
              <th class="py-3 text-right font-medium">Jami</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in myClients" :key="c.id" class="border-b border-slate-50 last:border-0">
              <td class="py-3 pr-4 font-medium text-slate-900">
                {{ c.name }}
                <span v-if="c.vip" class="ml-1 rounded bg-amber-50 px-1.5 py-0.5 text-[10px] font-bold text-amber-600">VIP</span>
              </td>
              <td class="py-3 pr-4 text-slate-600">{{ c.phone }}</td>
              <td class="py-3 pr-4 text-slate-600">{{ c.lastTour || '—' }}</td>
              <td class="py-3 pr-4 text-slate-600">{{ c.trips }} ta</td>
              <td class="py-3 pr-4"><StatusBadge :status="c.status" /></td>
              <td class="py-3 text-right font-semibold text-slate-900">{{ money(c.total) }}</td>
            </tr>
            <tr v-if="!myClients.length">
              <td colspan="6" class="py-12 text-center text-sm text-slate-500">Hozircha mijoz yo'q.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </PanelCard>

    <!-- ——— FAOLIYATIM ——— -->
    <PanelCard v-else title="Faoliyat tarixi">
      <ol v-if="myActivity.length" class="relative space-y-4 border-l border-slate-200 pl-5">
        <li v-for="a in myActivity" :key="a.id" class="relative">
          <span class="absolute -left-[26px] top-1.5 h-2.5 w-2.5 rounded-full ring-4 ring-white"
                :class="ACTION_TONE[a.action]?.dot || 'bg-slate-300'" />
          <div class="flex flex-wrap items-baseline justify-between gap-2">
            <p class="text-sm font-medium text-slate-800">{{ activityText(a) }}</p>
            <p class="text-xs text-slate-400">{{ whenText(a.ts) }}</p>
          </div>
          <p class="text-sm text-slate-500">{{ a.title }}</p>
          <p v-if="a.meta?.amount" class="text-xs font-semibold text-emerald-600">{{ money(a.meta.amount) }}</p>
          <p v-if="isAdmin" class="text-[11px] text-slate-400">{{ a.actor }}</p>
        </li>
      </ol>
      <p v-else class="py-12 text-center text-sm text-slate-500">
        Hozircha faoliyat yo'q. Lead qo'shing yoki bosqichini o'zgartiring — bu yerda aks etadi.
      </p>
    </PanelCard>

    <!-- ——— Tahrirlash oynasi ——— -->
    <ModalDialog :open="editOpen" title="Profilni tahrirlash"
                 @close="editOpen = false" @submit="saveProfile">
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="Ism Familiya">
          <input v-model="draft.name" class="field" placeholder="Ism Familiya" />
        </FormField>
        <FormField label="Email">
          <input v-model="draft.email" type="email" class="field" placeholder="pochta@sadaf.uz" />
        </FormField>
        <FormField label="Telefon">
          <PhoneInput v-model="draft.phone" />
        </FormField>
      </div>
      <p v-if="saveError" class="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">
        {{ saveError }}
      </p>
    </ModalDialog>
  </div>
</template>
