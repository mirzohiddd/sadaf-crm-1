<script setup>
import { ref, computed, onMounted } from 'vue'
import PanelCard from '@/components/PanelCard.vue'
import AreaChart from '@/components/AreaChart.vue'
import BarChart from '@/components/BarChart.vue'
import DonutChart from '@/components/DonutChart.vue'
import FunnelChart from '@/components/FunnelChart.vue'
import GaugeChart from '@/components/GaugeChart.vue'
import MetricTile from '@/components/MetricTile.vue'
import AppIcon from '@/components/AppIcon.vue'
import { db, loadAnalytics, isSuperAdmin } from '@/store'
import { leadStageList, leadSourceNames } from '@/data/mock.js'
import { money } from '@/utils/format.js'

const WON = ['Bron tasdiqlandi', "To'lov qilindi"]
const LOST = ['Bekor qilindi', 'Sifatsiz lead']
const BOOKING_STAGE = 'Bron tasdiqlandi'
const SALE_STAGE = "To'lov qilindi"

const sum = (arr, f) => arr.reduce((s, x) => s + Number(f(x) || 0), 0)

// Oylik maqsad — sozlanadigan qiymat
const target = ref(50000)

// Backend agregatlari (funnel, menejerlar) yangilanib turishi uchun
onMounted(loadAnalytics)

const wonLeads = computed(() => db.leads.filter((l) => WON.includes(l.stage)))
const revenue = computed(() => sum(wonLeads.value, (l) => l.amount))

// ——— Sana yordamchilari (backenddagi 'dd.mm.yyyy' formatiga mos) ———

const parseUzDate = (str) => {
  if (!str) return null
  const [d, m, y] = String(str).split('.')
  if (!d || !m || !y) return null
  const date = new Date(Number(y), Number(m) - 1, Number(d))
  return Number.isNaN(date.getTime()) ? null : date
}

const isToday = (str) => {
  const d = parseUzDate(str)
  const now = new Date()
  return !!d && d.toDateString() === now.toDateString()
}

const isThisMonth = (str) => {
  const d = parseUzDate(str)
  const now = new Date()
  return !!d && d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth()
}

// ——— Bugungi va oylik ko'rsatkichlar ———

const todayLeadsCount = computed(() => db.leads.filter((l) => isToday(l.date)).length)
const todayBookingsCount = computed(
  () => db.leads.filter((l) => l.stage === BOOKING_STAGE && isToday(l.date)).length
)
const todaySalesCount = computed(
  () => db.leads.filter((l) => l.stage === SALE_STAGE && isToday(l.date)).length
)
const todayRevenue = computed(() => sum(wonLeads.value.filter((l) => isToday(l.date)), (l) => l.amount))

const monthSalesCount = computed(
  () => db.leads.filter((l) => l.stage === SALE_STAGE && isThisMonth(l.date)).length
)
const monthRevenue = computed(() => sum(wonLeads.value.filter((l) => isThisMonth(l.date)), (l) => l.amount))

// ——— Analytics Forecast — mavjud (won) savdo tarixidan chiziqli trend orqali ———
//
// Faqat haqiqiy CRM ma'lumotlaridan (wonLeads) hisoblanadi, tasodifiy son
// ishlatilmaydi. Super Admin uchun db.leads allaqachon barcha adminlar
// bo'yicha to'liq (scoped backend orqali), oddiy Admin uchun esa faqat
// o'ziga tegishli leadlar — forecast ham shu doirada hisoblanadi.

const MONTH_LABELS = [
  'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
  'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'
]

const now = new Date()
const currentYear = now.getFullYear()
const currentMonthIdx = now.getMonth() // 0-asosli (0 = Yanvar)

// Har bir oy uchun haqiqiy (won) savdo summasi — xronologik tartibda.
// Faqat haqiqatda ma'lumot mavjud bo'lgan (o'tgan/joriy) oylar kiradi.
const monthlyHistory = computed(() => {
  const map = {}
  wonLeads.value.forEach((l) => {
    const d = parseUzDate(l.date)
    if (!d) return
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    map[key] = (map[key] || 0) + Number(l.amount || 0)
  })
  return Object.keys(map)
    .sort()
    .map((key) => {
      const [y, m] = key.split('-').map(Number)
      return { key, year: y, month: m - 1, revenue: map[key] }
    })
})

const hasHistory = computed(() => monthlyHistory.value.length > 0)

// Chiziqli regressiya (eng kichik kvadratlar usuli) — oy indeksi (x) bo'yicha
// savdo (y) trendi. 1 oylik tarix bo'lsa trend hisoblanmaydi, shu oy
// bazaviy qiymat sifatida olinadi (baribir haqiqiy raqam, tasodifiy emas).
const trend = computed(() => {
  const rows = monthlyHistory.value
  const n = rows.length
  if (n === 0) return null
  if (n === 1) return { slope: 0, intercept: rows[0].revenue }
  const xs = rows.map((_, i) => i)
  const ys = rows.map((r) => r.revenue)
  const sumX = sum(xs, (x) => x)
  const sumY = sum(ys, (y) => y)
  const sumXY = xs.reduce((s, x, i) => s + x * ys[i], 0)
  const sumXX = xs.reduce((s, x) => s + x * x, 0)
  const denom = n * sumXX - sumX * sumX
  const slope = denom ? (n * sumXY - sumX * sumY) / denom : 0
  const intercept = (sumY - slope * sumX) / n
  return { slope, intercept }
})

// Tarixdagi indeksdan keyingi (index) oy uchun bashorat — manfiy bo'lmaydi
const forecastAt = (index) => {
  const t = trend.value
  if (!t) return 0
  return Math.max(0, Math.round(t.slope * index + t.intercept))
}

// Kelasi oy uchun kutilayotgan savdo
const nextMonthDate = computed(() => {
  const m = currentMonthIdx + 1
  return new Date(currentYear + Math.floor(m / 12), m % 12, 1)
})
const nextMonthForecast = computed(() => forecastAt(monthlyHistory.value.length))

// Joriy yilda haqiqiy ro'yxatga olingan (real) savdo
const ytdActual = computed(() =>
  sum(monthlyHistory.value.filter((r) => r.year === currentYear), (r) => r.revenue)
)

// Joriy oydan dekabrgacha qolgan oylar uchun bashorat yig'indisi
const remainingMonthsForecast = computed(() => {
  const rows = monthlyHistory.value
  const startIndex = rows.length
  const monthsLeft = Math.max(0, 11 - currentMonthIdx)
  let total = 0
  for (let i = 0; i < monthsLeft; i++) total += forecastAt(startIndex + i)
  return total
})

// Yil oxirigacha kutilayotgan jami savdo = joriy yilgi real + qolgan oylar bashorati
const yearEndForecast = computed(() => ytdActual.value + remainingMonthsForecast.value)

// Oylar bo'yicha grafik uchun ma'lumot: real (o'tgan/joriy) + bashorat (kelasi, yil oxirigacha)
const forecastChart = computed(() => {
  const rows = monthlyHistory.value
  const bars = rows.map((r) => ({
    key: r.key,
    label: `${MONTH_LABELS[r.month].slice(0, 3)} ${String(r.year).slice(2)}`,
    value: r.revenue,
    type: 'real'
  }))
  const startIndex = rows.length
  const monthsLeft = Math.max(0, 11 - currentMonthIdx)
  for (let i = 0; i < monthsLeft; i++) {
    const d = new Date(currentYear, currentMonthIdx + 1 + i, 1)
    bars.push({
      key: `f-${d.getFullYear()}-${d.getMonth()}`,
      label: `${MONTH_LABELS[d.getMonth()].slice(0, 3)} ${String(d.getFullYear()).slice(2)}`,
      value: forecastAt(startIndex + i),
      type: 'forecast'
    })
  }
  return bars
})

const forecastChartMax = computed(() =>
  forecastChart.value.length ? Math.max(...forecastChart.value.map((b) => b.value), 1) : 1
)

// ——— Target va real farqi (joriy oy) ———

const currentMonthActual = computed(() => {
  const row = monthlyHistory.value.find((r) => r.year === currentYear && r.month === currentMonthIdx)
  return row ? row.revenue : 0
})
const targetDiff = computed(() => currentMonthActual.value - target.value)
const targetDiffPct = computed(() =>
  target.value ? ((targetDiff.value / target.value) * 100).toFixed(1) + '%' : '0%'
)

const kpi = computed(() => {
  const leads = db.leads
  return {
    leads: leads.length,
    pipeline: money(sum(leads, (l) => l.amount)),
    revenue: money(revenue.value),
    conversion: leads.length ? ((wonLeads.value.length / leads.length) * 100).toFixed(1) + '%' : '0%',
    avg: money(wonLeads.value.length ? Math.round(revenue.value / wonLeads.value.length) : 0),
    lost: leads.filter((l) => LOST.includes(l.stage)).length
  }
})

// ——— Savdo dinamikasi: sana bo'yicha yopilgan summalar ———

const salesByDate = computed(() => {
  const map = {}
  wonLeads.value.forEach((l) => { map[l.date] = (map[l.date] || 0) + Number(l.amount || 0) })

  const keys = Object.keys(map).sort((a, b) => {
    const [d1, m1, y1] = a.split('.')
    const [d2, m2, y2] = b.split('.')
    return new Date(y1, m1 - 1, d1) - new Date(y2, m2 - 1, d2)
  })

  return { labels: keys, points: keys.map((k) => map[k]) }
})

// ——— Manbalar ———

const bySource = computed(() =>
  leadSourceNames
    .map((s) => ({ label: s, value: db.leads.filter((l) => l.source === s).length }))
    .filter((x) => x.value > 0)
)

const SOURCE_COLORS = { Telegram: '#3b82f6', Instagram: '#ec4899', Sayt: '#10b981', "Qo'ng'iroq": '#f59e0b' }

const sourceDonut = computed(() =>
  bySource.value.map((s) => ({ ...s, color: SOURCE_COLORS[s.label] || '#94a3b8' }))
)

// ——— Voronka ———

const funnel = computed(() => {
  const order = leadStageList.map((s) => s.name).filter((n) => !LOST.includes(n))
  const rows = order.map((name) => ({
    label: name,
    value: db.leads.filter((l) => l.stage === name).length
  }))
  return rows.some((r) => r.value > 0) ? rows : []
})

// ——— Adminlar bo'yicha taqqoslash (faqat Super Admin ko'radi) ———
//
// Oddiy Admin uchun db.leads backend tomonidan allaqachon faqat o'ziga
// tegishli leadlar bilan cheklangan — shu sababli bu ro'yxat uning uchun
// avtomatik ravishda faqat o'z qatoridan iborat bo'ladi. Taqqoslash
// jadvali va grafigi shunga qaramay faqat Super Admin uchun ko'rsatiladi.

const managers = computed(() => {
  const map = {}
  db.leads.forEach((l) => {
    const m = l.manager || 'Biriktirilmagan'
    map[m] = map[m] || { leads: 0, bookings: 0, sales: 0, deals: 0, revenue: 0 }
    map[m].leads++
    if (l.stage === BOOKING_STAGE) map[m].bookings++
    if (l.stage === SALE_STAGE) map[m].sales++
    if (WON.includes(l.stage)) {
      map[m].deals++
      map[m].revenue += Number(l.amount || 0)
    }
  })
  return Object.entries(map)
    .map(([name, s]) => ({ name, ...s }))
    .sort((a, b) => b.revenue - a.revenue)
})

const managerBars = computed(() => managers.value.map((m) => ({ label: m.name.split(' ')[0], value: m.deals })))

// ——— Yo'nalishlar bo'yicha daromad ———

const byDirection = computed(() => {
  const map = {}
  wonLeads.value.forEach((l) => {
    const tour = db.tours.find((t) => t.name === l.tour)
    const key = tour?.country || l.tour || 'Boshqa'
    map[key] = (map[key] || 0) + Number(l.amount || 0)
  })
  return Object.entries(map).map(([name, amount]) => ({ name, amount })).sort((a, b) => b.amount - a.amount)
})

// ——— So'nggi harakatlar ———

const activity = computed(() => {
  const items = []

  db.leads.forEach((l) => items.push({
    icon: 'send', tone: 'bg-sky-50 text-sky-600',
    title: `${l.name} — ${l.stage}`,
    meta: `${l.source} · ${l.tour || '—'}`,
    amount: l.amount, date: l.date
  }))

  db.tasks.forEach((t) => items.push({
    icon: 'check-square', tone: 'bg-violet-50 text-violet-600',
    title: t.title,
    meta: `${t.from} → ${t.to}`,
    amount: 0, date: t.due
  }))

  db.clients.forEach((c) => items.push({
    icon: 'user', tone: 'bg-emerald-50 text-emerald-600',
    title: `${c.name} — mijoz`,
    meta: `${c.trips} sayohat · ${c.country}`,
    amount: c.total, date: c.lastDate
  }))

  return items.slice(0, 8)
})
</script>

<template>
  <div class="space-y-5">
    <!-- KPI qatori -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <MetricTile label="Jami leadlar" :value="kpi.leads" unit="ta" icon="users" color="blue" />
      <MetricTile label="Voronka summasi" :value="kpi.pipeline" icon="layers" color="violet" />
      <MetricTile label="Yopilgan daromad" :value="kpi.revenue" icon="dollar" color="teal" />
      <MetricTile label="Konversiya" :value="kpi.conversion" icon="chart" color="green" />
      <MetricTile label="O'rtacha bitim" :value="kpi.avg" icon="handshake" color="amber" />
      <MetricTile label="Yo'qotilgan" :value="kpi.lost" unit="ta" icon="x-circle" color="rose" />
    </div>


    <!-- Yuqori qator: dinamika + manbalar -->
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-3">
      <PanelCard title="Savdo dinamikasi" class="lg:col-span-2">
        <template #action>
          <span class="text-2xl font-bold text-slate-900">{{ kpi.revenue }}</span>
        </template>
        <AreaChart :points="salesByDate.points" :labels="salesByDate.labels" />
      </PanelCard>

      <PanelCard title="Manbalar bo'yicha leadlar">
        <template #action>
          <span class="text-2xl font-bold text-slate-900">{{ kpi.leads }}</span>
        </template>
        <DonutChart :data="sourceDonut" center-label="Leadlar" />
      </PanelCard>
    </div>

    <!-- O'rta qator: harakatlar + voronka + menejerlar -->
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-4">
      <PanelCard title="So'nggi harakatlar">
        <ul v-if="activity.length" class="max-h-[320px] space-y-2.5 overflow-y-auto">
          <li v-for="(a, i) in activity" :key="i" class="flex items-start gap-2.5">
            <span class="grid h-8 w-8 shrink-0 place-items-center rounded-lg" :class="a.tone">
              <AppIcon :name="a.icon" class="h-4 w-4" />
            </span>
            <span class="min-w-0 flex-1">
              <span class="block truncate text-sm text-slate-800">{{ a.title }}</span>
              <span class="block truncate text-xs text-slate-400">{{ a.meta }}</span>
            </span>
            <span class="shrink-0 text-right">
              <span v-if="a.amount" class="block text-sm font-semibold text-slate-900">{{ money(a.amount) }}</span>
              <span class="block text-xs text-slate-400">{{ a.date || '—' }}</span>
            </span>
          </li>
        </ul>
        <p v-else class="py-10 text-center text-sm text-slate-400">Ma'lumot yo'q</p>
      </PanelCard>

      <PanelCard title="Konversiya voronkasi" :class="isSuperAdmin ? 'lg:col-span-2' : 'lg:col-span-3'">
        <FunnelChart :data="funnel" />
      </PanelCard>

      <PanelCard v-if="isSuperAdmin" title="Adminlar bitimlari">
        <BarChart :data="managerBars" />
      </PanelCard>
    </div>

    <!-- Pastki qator: maqsad + yo'nalishlar + manba ustunlari -->
    <div class="grid grid-cols-1 gap-5 lg:grid-cols-4">
      <PanelCard title="Oylik maqsad">
        <GaugeChart :value="revenue" :target="target" :format="money" label="Oylik daromad rejasi" />
        <div class="mt-4 flex items-center gap-2">
          <label for="target" class="shrink-0 text-xs text-slate-500">Maqsad ($)</label>
          <input id="target" v-model.number="target" type="number" min="0" step="1000"
                 class="field py-1.5 text-sm" />
        </div>
      </PanelCard>

      <PanelCard title="Yo'nalishlar bo'yicha daromad" class="lg:col-span-2">
        <ul v-if="byDirection.length" class="divide-y divide-slate-100">
          <li v-for="d in byDirection" :key="d.name"
              class="flex items-center gap-3 py-3 text-sm first:pt-0 last:pb-0">
            <span class="grid h-9 w-9 place-items-center rounded-lg bg-sky-50 text-sky-600">
              <AppIcon name="globe" class="h-4 w-4" />
            </span>
            <span class="text-slate-700">{{ d.name }}</span>
            <span class="ml-auto font-semibold text-slate-900">{{ money(d.amount) }}</span>
          </li>
        </ul>
        <p v-else class="py-10 text-center text-sm text-slate-400">Ma'lumot yo'q</p>
      </PanelCard>

      <PanelCard title="Manbalar taqsimoti">
        <BarChart :data="bySource" />
      </PanelCard>
    </div>

    <!-- ——— Analytics Forecast — real savdo tarixi asosidagi bashorat ——— -->
    <PanelCard title="Savdo prognozi">
      <div v-if="!hasHistory" class="py-10 text-center text-sm text-slate-400">
        Prognoz chiqarish uchun yetarli savdo tarixi yo'q.
      </div>

      <template v-else>
        <!-- KPI: real vs forecast -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricTile label="Real savdo (joriy oy)" :value="money(currentMonthActual)" icon="dollar" color="teal" />
          <MetricTile
            :label="`Kutilayotgan (${MONTH_LABELS[nextMonthDate.getMonth()]})`"
            :value="money(nextMonthForecast)" icon="chart" color="amber" />
          <MetricTile :label="`Real savdo (${currentYear})`" :value="money(ytdActual)" icon="dollar" color="teal" />
          <MetricTile label="Yil oxirigacha kutilayotgan" :value="money(yearEndForecast)" icon="chart" color="violet" />
        </div>

        <!-- Target va real farqi -->
        <div class="mt-4 flex flex-wrap items-center gap-x-6 gap-y-2 rounded-xl bg-slate-50 px-4 py-3 text-sm">
          <span class="text-slate-500">Oylik maqsad: <b class="text-slate-800">{{ money(target) }}</b></span>
          <span class="text-slate-500">Real (joriy oy): <b class="text-slate-800">{{ money(currentMonthActual) }}</b></span>
          <span :class="targetDiff >= 0 ? 'text-emerald-600' : 'text-rose-500'" class="font-semibold">
            Farq: {{ targetDiff >= 0 ? '+' : '−' }}{{ money(Math.abs(targetDiff)) }} ({{ targetDiff >= 0 ? '+' : '' }}{{ targetDiffPct }})
          </span>
        </div>

        <!-- Oylar bo'yicha grafik: real + bashorat -->
        <div class="mt-5">
          <div class="mb-2 flex items-center gap-4 text-xs text-slate-500">
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-blue-500"></span>Real</span>
            <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-amber-400"></span>Bashorat</span>
          </div>
          <div class="flex items-end gap-2 overflow-x-auto pb-2">
            <div v-for="b in forecastChart" :key="b.key" class="flex w-14 shrink-0 flex-col items-center gap-1.5">
              <span class="text-[11px] font-medium text-slate-600">
                {{ b.value >= 1000 ? Math.round(b.value / 1000) + 'k' : b.value }}
              </span>
              <div class="flex h-32 w-8 items-end overflow-hidden rounded-md bg-slate-100">
                <div
                  class="w-full rounded-md transition-all"
                  :class="b.type === 'real' ? 'bg-blue-500' : 'bg-amber-400'"
                  :style="{ height: (b.value / forecastChartMax) * 100 + '%' }"
                />
              </div>
              <span class="text-[11px] text-slate-400">{{ b.label }}</span>
            </div>
          </div>
        </div>
      </template>
    </PanelCard>

    <!-- Adminlar bo'yicha taqqoslash — faqat Super Admin ko'radi.
         Oddiy Admin faqat o'z statistikasini (yuqoridagi KPI kartalari) ko'radi. -->
    <template v-if="isSuperAdmin">
      <PanelCard title="Menejerlar bo'yicha taqqoslash jadvali">
        <div v-if="managers.length" class="overflow-x-auto">
          <table class="w-full min-w-[680px] text-sm">
            <thead>
              <tr class="border-b border-slate-100 text-left text-xs uppercase tracking-wide text-slate-500">
                <th class="py-2.5 font-medium">Menejer</th>
                <th class="py-2.5 text-right font-medium">Leadlar</th>
                <th class="py-2.5 text-right font-medium">Bronlar</th>
                <th class="py-2.5 text-right font-medium">Savdo</th>
                <th class="py-2.5 text-right font-medium">Daromad</th>
                <th class="py-2.5 text-right font-medium">Ulush</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in managers" :key="m.name" class="border-b border-slate-50 last:border-0">
                <td class="py-3 font-medium text-slate-900">{{ m.name }}</td>
                <td class="py-3 text-right text-slate-600">{{ m.leads }}</td>
                <td class="py-3 text-right text-slate-600">{{ m.bookings }}</td>
                <td class="py-3 text-right text-slate-600">{{ m.sales }}</td>
                <td class="py-3 text-right font-semibold text-slate-900">{{ money(m.revenue) }}</td>
                <td class="py-3 text-right text-slate-500">
                  {{ revenue ? ((m.revenue / revenue) * 100).toFixed(1) + '%' : '0%' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="py-10 text-center text-sm text-slate-400">Ma'lumot yo'q</p>
      </PanelCard>
    </template>
  </div>
</template>