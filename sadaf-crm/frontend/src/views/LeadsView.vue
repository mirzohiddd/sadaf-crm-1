<script setup>
import { ref, computed, reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import MetricTile from '@/components/MetricTile.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import FormField from '@/components/FormField.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import SourceTag from '@/components/SourceTag.vue'
import ToolbarButton from '@/components/ToolbarButton.vue'
import AppIcon from '@/components/AppIcon.vue'
import {
  db, leadsApi, moveLead, isSuperAdmin, markLeadSeen,
  leadReminders, loadLeadReminders, clearLeadReminders, leadRemindersApi
} from '@/store'
import { leadStageList, leadStages, leadSourceNames } from '@/data/mock.js'
import { todayUz, money, exportCsv } from '@/utils/format.js'

const view = ref('kanban') // kanban | list
const query = ref('')
const sourceFilter = ref('')
const openMenu = ref(null)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return db.leads.filter((l) =>
    (!q || l.name.toLowerCase().includes(q) || l.phone.includes(q)) &&
    (!sourceFilter.value || l.source === sourceFilter.value)
  )
})

const byStage = (stage) => filtered.value.filter((l) => l.stage === stage)
const sumOf = (stage) => byStage(stage).reduce((s, l) => s + Number(l.amount || 0), 0)

const totals = computed(() => {
  const all = db.leads
  const booked = all.filter((l) => l.stage === 'Bron tasdiqlandi').length
  const paid = all.filter((l) => l.stage === "To'lov qilindi").length
  const lost = all.filter((l) => ['Bekor qilindi', 'Sifatsiz lead'].includes(l.stage)).length
  const won = all.filter((l) => ['Bron tasdiqlandi', "To'lov qilindi"].includes(l.stage))
  return {
    all: all.length,
    today: all.filter((l) => l.date === todayUz()).length,
    conversion: all.length ? ((booked / all.length) * 100).toFixed(1) + '%' : '0%',
    booked,
    paid,
    lost,
    revenue: money(won.reduce((s, l) => s + Number(l.amount || 0), 0)),
    pipeline: money(all.reduce((s, l) => s + Number(l.amount || 0), 0))
  }
})

// ——— Aloqa yordamchilari ———

// +998 77 700 71 17 -> 998777007117
const digits = (phone) => String(phone || '').replace(/\D/g, '')

const telLink = (phone) => `tel:+${digits(phone)}`

// Telegram: agar leadda username bo'lsa (@nick) — o'shanga, aks holda raqam bo'yicha
function tgLink(lead) {
  const u = (lead?.telegram || '').trim().replace(/^@/, '')
  if (u) return `https://t.me/${u}`
  return `https://t.me/+${digits(lead?.phone)}`
}

function openTelegram(lead) {
  window.open(tgLink(lead), '_blank', 'noopener')
}

function callLead(lead) {
  window.location.href = telLink(lead.phone)
}

// ——— Modal / forma ———

const emptyForm = () => ({
  id: null, name: '', phone: '', telegram: '', tour: '', people: '', amount: '',
  manager: '', comment: '', city: 'Toshkent', date: todayUz(), source: 'Telegram', stage: 'Yangi'
})

const modalOpen = ref(false)
const form = reactive(emptyForm())
const errors = reactive({})
const clearErrors = () => Object.keys(errors).forEach((k) => delete errors[k])

function openCreate(stage = 'Yangi') {
  Object.assign(form, emptyForm(), { stage })
  clearErrors()
  modalOpen.value = true
}

function openEdit(lead) {
  Object.assign(form, emptyForm(), { ...lead })
  clearErrors()
  openMenu.value = null
  modalOpen.value = true
  if (lead?.id != null) markLeadSeen(lead.id)
}

// Barcha maydonlar ixtiyoriy — forma har doim saqlanadi, validatsiya yo'q.
function validate() {
  clearErrors()
  return true
}

function save() {
  if (!validate()) return
  const payload = {
    ...form,
    people: form.people === '' ? 0 : Number(form.people) || 0,
    amount: form.amount === '' ? 0 : Number(form.amount) || 0
  }
  form.id ? leadsApi.update(payload) : leadsApi.add(payload)
  modalOpen.value = false
}

// ——— Bosqichni ko'chirish ———

const dragId = ref(null)
const dragOver = ref(null)

function onDrop(stage) {
  if (dragId.value != null) moveLead(dragId.value, stage)
  dragId.value = null
  dragOver.value = null
}

function setStage(lead, stage) {
  moveLead(lead.id, stage)
  openMenu.value = null
}

// ——— O'chirish ———

const toDelete = ref(null)

function confirmDelete() {
  if (selected.value === toDelete.value.id) selected.value = null
  leadsApi.remove(toDelete.value.id)
  toDelete.value = null
}

// ——— O'ng tomondagi detal paneli ———

const selected = ref(null)

const selectedLead = computed(() =>
  selected.value == null ? null : db.leads.find((l) => l.id === selected.value) || null
)

function openDetail(lead) {
  selected.value = lead.id
  openMenu.value = null
  markLeadSeen(lead.id)
  loadLeadReminders(lead.id)
}
const closeDetail = () => { selected.value = null; clearLeadReminders() }

function editFromPanel(lead) {
  selected.value = null
  openEdit(lead)
}

// Esc bosilganda panel yopiladi
function onKey(e) { if (e.key === 'Escape') closeDetail() }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))

// Lead o'chib ketsa panel ham yopiladi
watch(selectedLead, (v) => { if (selected.value != null && !v) selected.value = null })

// ——— Eslatma / Reminder (lead detal paneli ichida) ———

const showReminderForm = ref(false)
const reminderSaving = ref(false)
const reminderError = ref('')

function emptyReminderForm() {
  const d = new Date()
  d.setDate(d.getDate() + 1) // qulaylik uchun — ertangi sana oldindan tanlangan
  const p = (n) => String(n).padStart(2, '0')
  return { date: `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`, time: '09:00', note: '' }
}

const reminderForm = reactive(emptyReminderForm())

function toggleReminderForm() {
  showReminderForm.value = !showReminderForm.value
  reminderError.value = ''
  if (showReminderForm.value) Object.assign(reminderForm, emptyReminderForm())
}

// Vaqt har doim 24-soatlik "HH:MM" matn ko'rinishida saqlanadi. Bu native
// <input type="time"> o'rniga ishlatiladi, chunki uning AM/PM yoki 24-soat
// ko'rinishida chiqishi brauzer/OS tiliga bog'liq bo'lib, foydalanuvchi
// buni boshqara olmaydi. Matn maydoni esa har doim bir xil formatda ishlaydi.
const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/

// Kiritilayotganda raqamlarni avtomatik "HH:MM" ko'rinishiga keltiradi.
function onTimeInput(e) {
  const digits = e.target.value.replace(/\D/g, '').slice(0, 4)
  reminderForm.time = digits.length >= 3 ? `${digits.slice(0, 2)}:${digits.slice(2)}` : digits
}

async function submitReminder() {
  if (!reminderForm.date) {
    reminderError.value = 'Sanani tanlang.'
    return
  }
  if (!TIME_RE.test(reminderForm.time)) {
    reminderError.value = "Vaqtni to'g'ri kiriting (soat:daqiqa, masalan 14:30)."
    return
  }
  reminderError.value = ''
  reminderSaving.value = true
  const result = await leadRemindersApi.add(selectedLead.value.id, { ...reminderForm })
  reminderSaving.value = false
  if (!result.ok) {
    reminderError.value = result.message || "Eslatmani saqlab bo'lmadi. Qaytadan urinib ko'ring."
    return
  }
  showReminderForm.value = false
}

// Ro'yxatda ko'rsatish uchun "YYYY-MM-DD" -> "DD.MM.YYYY"
function fmtReminderDate(iso) {
  const [y, m, d] = String(iso || '').split('-')
  return y && m && d ? `${d}.${m}.${y}` : (iso || '')
}

function reminderOverdue(r) {
  if (r.done) return false
  const due = new Date(`${r.date}T${r.time || '00:00'}`)
  return !Number.isNaN(due.getTime()) && due.getTime() < Date.now()
}

const detailRows = computed(() => {
  const l = selectedLead.value
  if (!l) return []
  const rows = [
    { label: 'Telefon', value: l.phone, icon: 'phone', tone: 'text-emerald-600 bg-emerald-50' },
    { label: 'Manba', value: l.source, icon: 'message', tone: 'text-sky-600 bg-sky-50' },
    { label: 'Tur', value: `${l.tour} · ${l.people} kishi`, icon: 'layers', tone: 'text-violet-600 bg-violet-50' }
  ]
  // "Mas'ul odam" faqat Super Adminga ko'rinadi
  if (isSuperAdmin.value) {
    rows.push({ label: "Mas'ul", value: l.manager || '—', icon: 'user', tone: 'text-blue-600 bg-blue-50', strong: true })
  }
  rows.push(
    { label: 'Shahar', value: l.city || 'Toshkent', icon: 'map', tone: 'text-slate-600 bg-slate-100' },
    { label: 'Izoh', value: l.comment || '—', icon: 'chat', tone: 'text-amber-600 bg-amber-50' },
    { label: 'Sana', value: `${l.date}  ${l.time || ''}`.trim(), icon: 'calendar', tone: 'text-slate-600 bg-slate-100' }
  )
  // Google Sheets (Meta Lead Ads) orqali kelgan leadlarda qo'shimcha
  // maydonlar bo'ladi — mavjud bo'lganda ko'rsatiladi, bo'lmasa qatorlar
  // umuman qo'shilmaydi (eski/qo'lda kiritilgan leadlar o'zgarishsiz qoladi).
  if (l.campaign) rows.push({ label: 'Kampaniya', value: l.campaign, icon: 'chart', tone: 'text-indigo-600 bg-indigo-50' })
  if (l.ad) rows.push({ label: 'Reklama', value: l.ad, icon: 'image', tone: 'text-indigo-600 bg-indigo-50' })
  if (l.leadStatus) rows.push({ label: 'Meta holati', value: l.leadStatus, icon: 'check-circle', tone: 'text-teal-600 bg-teal-50' })
  // Landing (sadaf-landing) ariza formasidan kelgan qo'shimcha maydonlar —
  // mavjud bo'lganda ko'rsatiladi, bo'lmasa qatorlar umuman qo'shilmaydi.
  if (l.travelDate) rows.push({ label: 'Reja qilingan sana', value: l.travelDate, icon: 'calendar', tone: 'text-rose-600 bg-rose-50' })
  const utm = [l.utm_source, l.utm_medium, l.utm_campaign].filter(Boolean).join(' / ')
  if (utm) rows.push({ label: 'UTM', value: utm, icon: 'chart', tone: 'text-indigo-600 bg-indigo-50' })
  return rows
})

const detailHistory = computed(() => {
  const l = selectedLead.value
  if (!l) return []
  if (l.history?.length) return l.history
  return [
    { title: 'Lead yaratildi', date: `${l.date} ${l.time || ''}`.trim(), author: 'Menejer', text: '', color: 'bg-blue-500' },
    { title: l.stage, date: `${l.date} ${l.time || ''}`.trim(), author: l.manager || '—', text: l.comment || '', color: 'bg-emerald-500' }
  ]
})

// "Mas'ul" ustuni faqat Super Adminga eksport/jadvalda ko'rinadi
const exportColumns = computed(() => [
  { key: 'name', label: 'Leadlar' }, { key: 'phone', label: 'Telefon' },
  { key: 'source', label: 'Manba' }, { key: 'tour', label: 'Tur' },
  { key: 'people', label: 'Odam' }, { key: 'amount', label: 'Summa (USD)' },
  ...(isSuperAdmin.value ? [{ key: 'manager', label: "Mas'ul" }] : []),
  { key: 'date', label: 'Sana' }, { key: 'stage', label: 'Bosqich' }
])
</script>

<template>
  <div class="space-y-5 transition-[padding] duration-300" :class="selected ? 'xl:pr-[352px]' : ''"
    @click="openMenu = null">
    <!-- Asboblar paneli -->
    <div class="card flex flex-wrap items-center gap-2.5 p-3 sm:gap-3 sm:p-4">
      <div class="relative min-w-[220px] flex-1 sm:max-w-xs">
        <AppIcon name="search"
          class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input v-model="query" type="search" class="field pl-9" placeholder="Ism yoki telefon bo'yicha qidirish" />
      </div>

      <select v-model="sourceFilter" class="field w-auto min-w-[140px] sm:min-w-[160px]">
        <option value="">Barcha manbalar</option>
        <option v-for="s in leadSourceNames" :key="s" :value="s">{{ s }}</option>
      </select>

      <div class="ml-auto flex flex-wrap gap-2.5 sm:gap-3">
        <div class="flex overflow-hidden rounded-xl border border-slate-200">
          <button class="flex items-center gap-2 px-4 py-2.5 text-sm font-medium"
            :class="view === 'kanban' ? 'bg-slate-100 text-slate-900' : 'bg-white text-slate-600'"
            @click="view = 'kanban'">
            <AppIcon name="layers" class="h-4 w-4" /> Kanban
          </button>
          <button class="flex items-center gap-2 border-l border-slate-200 px-4 py-2.5 text-sm font-medium"
            :class="view === 'list' ? 'bg-slate-100 text-slate-900' : 'bg-white text-slate-600'" @click="view = 'list'">
            <AppIcon name="bars" class="h-4 w-4" /> Ro'yxat
          </button>
        </div>

        <ToolbarButton icon="download" @click="exportCsv('ledlar.csv', exportColumns, filtered)">Export</ToolbarButton>
        <ToolbarButton icon="plus" variant="primary" @click="openCreate()">Yangi lead</ToolbarButton>
      </div>
    </div>

    <!-- Kanban -->
    <div v-if="view === 'kanban'" class="overflow-x-auto pb-3">
      <div class="flex min-w-max gap-3">
        <section v-for="col in leadStageList" :key="col.name" class="flex w-[264px] shrink-0 flex-col sm:w-[272px]"
          @dragover.prevent="dragOver = col.name" @dragleave="dragOver = null" @drop="onDrop(col.name)">
          <header :class="col.head" class="flex items-center gap-2 rounded-t-xl px-3.5 py-2.5 text-white">
            <AppIcon :name="col.icon" class="h-4 w-4 shrink-0 opacity-90" />
            <h2 class="truncate text-[13px] font-semibold uppercase tracking-wide">{{ col.name }}</h2>
            <span class="ml-auto rounded-md bg-black/20 px-1.5 py-0.5 text-xs font-semibold">
              {{ byStage(col.name).length }}
            </span>
          </header>

          <div class="border-x border-slate-200 bg-white px-3 pb-2 pt-3 text-center">
            <span class="inline-block rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-semibold text-slate-800">
              {{ money(sumOf(col.name)) }}
            </span>
          </div>

          <div
            class="flex-1 space-y-2.5 rounded-b-xl border-x border-b border-slate-200 bg-slate-50/80 p-2.5 transition-colors"
            :class="dragOver === col.name ? 'bg-blue-50 ring-2 ring-inset ring-blue-300' : ''">
            <button
              class="flex w-full items-center justify-center gap-1.5 rounded-lg border border-dashed border-slate-300 bg-white py-2 text-sm text-slate-500 hover:border-blue-400 hover:text-blue-600"
              @click.stop="openCreate(col.name)">
              <AppIcon name="plus" class="h-4 w-4" /> Lead qo'shish
            </button>

            <article v-for="lead in byStage(col.name)" :key="lead.id" draggable="true"
              class="animate-pop-in cursor-pointer rounded-lg border border-l-4 border-slate-200 bg-white p-3 shadow-sm transition hover:shadow-md active:cursor-grabbing"
              :class="[col.edge, selected === lead.id ? 'ring-2 ring-blue-500 ring-offset-1' : '']"
              @dragstart="dragId = lead.id" @click.stop="openDetail(lead)">
              <div class="flex items-start justify-between gap-2">
                <p class="text-xs font-medium text-slate-400">#{{ lead.id }} · {{ lead.date }}</p>

                <div class="relative">
                  <button class="rounded-md p-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                    aria-label="Amallar" @click.stop="openMenu = openMenu === lead.id ? null : lead.id">
                    <AppIcon name="dots" class="h-4 w-4" />
                  </button>

                  <div v-if="openMenu === lead.id"
                    class="absolute right-0 z-20 mt-1 w-52 rounded-xl border border-slate-100 bg-white py-1.5 shadow-xl"
                    @click.stop>
                    <button class="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                      @click="openEdit(lead)">Tahrirlash</button>
                    <p class="px-4 pb-1 pt-2 text-xs font-medium uppercase text-slate-400">Bosqichga ko'chirish</p>
                    <button v-for="s in leadStages.filter((x) => x !== lead.stage)" :key="s"
                      class="block w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-50"
                      @click="setStage(lead, s)">{{ s }}</button>
                    <button
                      class="mt-1 block w-full border-t border-slate-100 px-4 py-2 text-left text-sm text-rose-600 hover:bg-rose-50"
                      @click="toDelete = lead; openMenu = null">O'chirish</button>
                  </div>
                </div>
              </div>

              <p class="mt-1.5 text-base font-bold text-slate-900">{{ money(lead.amount) }}</p>
              <p class="mt-1 text-sm font-medium text-blue-700">{{ lead.name }}</p>
              <p class="text-xs text-slate-500">{{ lead.phone }}</p>

              <dl class="mt-2.5 space-y-1.5 border-t border-slate-100 pt-2.5 text-xs">
                <div>
                  <dt class="text-slate-400">Tur</dt>
                  <dd class="text-slate-700">{{ lead.tour }} · {{ lead.people }} kishi</dd>
                </div>
                <div v-if="isSuperAdmin">
                  <dt class="text-slate-400">Mas'ul</dt>
                  <dd class="text-slate-700">{{ lead.manager || '—' }}</dd>
                </div>
              </dl>

              <div class="mt-2.5 flex items-center justify-between border-t border-slate-100 pt-2.5">
                <SourceTag :source="lead.source" />
                <span class="flex gap-1">
                  <a :href="telLink(lead.phone)"
                    class="grid h-7 w-7 place-items-center rounded-md bg-emerald-50 text-emerald-600 hover:bg-emerald-100"
                    title="Qo'ng'iroq qilish" @click.stop>
                    <AppIcon name="phone" class="h-3.5 w-3.5" />
                  </a>
                  <a :href="tgLink(lead)" target="_blank" rel="noopener"
                    class="grid h-7 w-7 place-items-center rounded-md bg-sky-50 text-sky-600 hover:bg-sky-100"
                    title="Telegramda yozish" @click.stop>
                    <AppIcon name="telegram" class="h-3.5 w-3.5" />
                  </a>
                </span>
              </div>
            </article>
          </div>
        </section>
      </div>
    </div>

    <!-- Ro'yxat ko'rinishi -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full min-w-[960px] text-sm">
          <thead>
            <tr
              class="border-b border-slate-100 bg-slate-50/70 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="px-5 py-3 font-medium">Leadlar</th>
              <th class="px-5 py-3 font-medium">Telefon</th>
              <th class="px-5 py-3 font-medium">Manba</th>
              <th class="px-5 py-3 font-medium">Tur</th>
              <th class="px-5 py-3 text-right font-medium">Summa</th>
              <th v-if="isSuperAdmin" class="px-5 py-3 font-medium">Mas'ul</th>
              <th class="px-5 py-3 font-medium">Sana</th>
              <th class="px-5 py-3 font-medium">Bosqich</th>
              <th class="px-5 py-3 text-right font-medium">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="l in filtered" :key="l.id"
              class="cursor-pointer border-b border-slate-50 last:border-0 hover:bg-slate-50/60"
              :class="selected === l.id ? 'bg-blue-50/60' : ''" @click="openDetail(l)">
              <td class="px-5 py-3.5 font-medium text-slate-900">{{ l.name }}</td>
              <td class="px-5 py-3.5 text-slate-600">{{ l.phone }}</td>
              <td class="px-5 py-3.5">
                <SourceTag :source="l.source" />
              </td>
              <td class="px-5 py-3.5 text-slate-600">{{ l.tour }}</td>
              <td class="px-5 py-3.5 text-right font-semibold text-slate-900">{{ money(l.amount) }}</td>
              <td v-if="isSuperAdmin" class="px-5 py-3.5 text-slate-600">{{ l.manager || '—' }}</td>
              <td class="px-5 py-3.5 text-slate-600">{{ l.date }}</td>
              <td class="px-5 py-3.5">
                <StatusBadge :status="l.stage" />
              </td>
              <td class="px-5 py-3.5">
                <div class="flex justify-end gap-2">
                  <a :href="telLink(l.phone)" title="Qo'ng'iroq"
                    class="grid h-9 w-9 place-items-center rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-100"
                    @click.stop>
                    <AppIcon name="phone" class="h-4 w-4" />
                  </a>
                  <a :href="tgLink(l)" target="_blank" rel="noopener" title="Telegram"
                    class="grid h-9 w-9 place-items-center rounded-lg bg-sky-50 text-sky-600 hover:bg-sky-100"
                    @click.stop>
                    <AppIcon name="telegram" class="h-4 w-4" />
                  </a>
                  <button class="grid h-9 w-9 place-items-center rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100"
                    title="Tahrirlash" @click.stop="openEdit(l)">
                    <AppIcon name="pencil" class="h-4 w-4" />
                  </button>
                  <button class="grid h-9 w-9 place-items-center rounded-lg bg-rose-50 text-rose-600 hover:bg-rose-100"
                    title="O'chirish" @click.stop="toDelete = l">
                    <AppIcon name="trash" class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!filtered.length">
              <td :colspan="isSuperAdmin ? 9 : 8" class="px-5 py-12 text-center text-sm text-slate-500">Leadlar
                topilmadi.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Umumiy ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <MetricTile label="Jami leadlar" :value="totals.all" unit="ta" icon="users" color="blue" />
      <MetricTile label="Bugungi leadlar" :value="totals.today" unit="ta" icon="user" color="violet" />
      <MetricTile label="Yo'qotilgan" :value="totals.lost" unit="ta" icon="x-circle" color="rose" />
      <MetricTile label="Konversiya" :value="totals.conversion" icon="chart" color="green" />
      <MetricTile label="Voronka summasi" :value="totals.pipeline" icon="layers" color="amber" />
      <MetricTile label="Yopilgan summa" :value="totals.revenue" icon="dollar" color="teal" />
    </div>

    <!-- ————— O'NG TOMONDAGI DETAL PANELI ————— -->
    <!-- Mobil uchun fon -->
    <Transition enter-active-class="transition duration-200" enter-from-class="opacity-0"
      leave-active-class="transition duration-150" leave-to-class="opacity-0">
      <div v-if="selectedLead" class="fixed inset-0 z-20 bg-slate-900/30 xl:hidden" @click="closeDetail" />
    </Transition>

    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="translate-x-full opacity-0"
      leave-active-class="transition duration-200 ease-in" leave-to-class="translate-x-full opacity-0">
      <!-- top-[73px] = TopNavbar balandligi. z-20 => navbar (z-30) tepada ko'rinib turadi -->
      <aside v-if="selectedLead"
        class="fixed right-0 top-[73px] z-20 flex h-[calc(100vh-73px)] w-[340px] max-w-[92vw] flex-col border-l border-slate-200 bg-white shadow-2xl"
        @click.stop>
        <header class="flex items-start justify-between gap-3 border-b border-slate-100 px-4 py-3">
          <div class="min-w-0">
            <h2 class="truncate text-base font-semibold text-slate-900">{{ selectedLead.name }}</h2>
            <div class="mt-1 flex items-center gap-2 text-[11px] text-slate-400">
              <span>#{{ selectedLead.id }}</span><span>·</span><span>{{ selectedLead.date }}</span>
              <StatusBadge :status="selectedLead.stage" />
            </div>
          </div>
          <button class="shrink-0 rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="Yopish" @click="closeDetail">
            <AppIcon name="close" class="h-4 w-4" />
          </button>
        </header>

        <!-- Tezkor amallar: TEPADA, hech qachon pastga tushib ketmaydi -->
        <div class="grid grid-cols-2 gap-2 border-b border-slate-100 px-4 py-3">
          <a :href="telLink(selectedLead.phone)"
            class="flex items-center justify-center gap-1.5 whitespace-nowrap rounded-lg bg-emerald-500 px-2 py-2 text-xs font-semibold text-white hover:bg-emerald-600">
            <AppIcon name="phone" class="h-4 w-4 shrink-0" /> Qo'ng'iroq
          </a>
          <a :href="tgLink(selectedLead)" target="_blank" rel="noopener"
            class="flex items-center justify-center gap-1.5 whitespace-nowrap rounded-lg bg-sky-500 px-2 py-2 text-xs font-semibold text-white hover:bg-sky-600">
            <AppIcon name="telegram" class="h-4 w-4 shrink-0" /> Telegram
          </a>
          <button
            class="col-span-2 flex items-center justify-center gap-1.5 rounded-lg border border-slate-200 px-2 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
            @click="editFromPanel(selectedLead)">
            <AppIcon name="pencil" class="h-4 w-4" /> Tahrirlash
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-4 py-4">
          <p class="text-2xl font-bold tracking-tight text-slate-900">{{ money(selectedLead.amount) }}</p>
          <p class="text-[11px] text-slate-400">Taxminiy summa</p>

          <dl class="mt-3 divide-y divide-slate-100 rounded-xl border border-slate-200">
            <div v-for="r in detailRows" :key="r.label" class="flex items-start gap-2 px-3 py-2">
              <dt class="w-16 shrink-0 text-[11px] text-slate-400">{{ r.label }}</dt>
              <dd class="flex-1 break-words text-right text-[13px] text-slate-700"
                :class="r.strong ? 'font-semibold text-slate-900' : ''">{{ r.value }}</dd>
              <span class="grid h-6 w-6 shrink-0 place-items-center rounded-md" :class="r.tone">
                <AppIcon :name="r.icon" class="h-3.5 w-3.5" />
              </span>
            </div>
          </dl>

          <!-- ⏰ Eslatmalar (Reminder) -->
          <div class="mt-5 flex items-center justify-between">
            <h3 class="text-sm font-semibold text-slate-900">⏰ Eslatmalar</h3>
            <button class="inline-flex items-center gap-1 rounded-lg bg-amber-50 px-2.5 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-100"
              @click="toggleReminderForm">
              <AppIcon :name="showReminderForm ? 'close' : 'plus'" class="h-3.5 w-3.5" />
              {{ showReminderForm ? 'Yopish' : "Eslatma qo'yish" }}
            </button>
          </div>

          <!-- Yangi eslatma formasi -->
          <div v-if="showReminderForm" class="mt-2.5 space-y-2.5 rounded-xl border border-amber-100 bg-amber-50/50 p-3">
            <div class="grid grid-cols-2 gap-2">
              <input v-model="reminderForm.date" type="date" class="field bg-white py-2 text-sm" />
              <input :value="reminderForm.time" @input="onTimeInput" type="text" inputmode="numeric"
                maxlength="5" placeholder="14:30" class="field bg-white py-2 text-sm" />
            </div>
            <textarea v-model="reminderForm.note" rows="2" class="field resize-y bg-white py-2 text-sm"
              placeholder="Izoh (masalan: qo'ng'iroq qilish, taklif yuborish...)" />
            <p v-if="reminderError" class="text-xs text-rose-600">{{ reminderError }}</p>
            <button class="w-full rounded-lg bg-amber-500 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-60"
              :disabled="reminderSaving" @click="submitReminder">
              {{ reminderSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
            </button>
          </div>

          <!-- Eslatmalar ro'yxati -->
          <ul v-if="leadReminders.items.length" class="mt-2.5 space-y-2">
            <li v-for="r in leadReminders.items" :key="r.id"
              class="flex items-start gap-2.5 rounded-xl border px-3 py-2.5"
              :class="r.done ? 'border-slate-100 bg-slate-50' : (reminderOverdue(r) ? 'border-rose-200 bg-rose-50/50' : 'border-slate-200 bg-white')">
              <button class="mt-0.5 grid h-5 w-5 shrink-0 place-items-center rounded-md border-2 transition"
                :class="r.done ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300 hover:border-amber-400'"
                :aria-label="r.done ? 'Bajarilmagan deb belgilash' : 'Bajarildi deb belgilash'"
                @click="leadRemindersApi.toggle(r.id)">
                <AppIcon v-if="r.done" name="check-circle" class="h-3.5 w-3.5" />
              </button>

              <span class="min-w-0 flex-1">
                <span class="flex items-center gap-1.5 text-[12px] font-medium"
                  :class="r.done ? 'text-slate-400 line-through' : (reminderOverdue(r) ? 'text-rose-600' : 'text-slate-800')">
                  <AppIcon name="clock" class="h-3 w-3 shrink-0" />
                  {{ fmtReminderDate(r.date) }} · {{ r.time }}
                  <span v-if="reminderOverdue(r)" class="badge bg-rose-100 text-rose-700">Kechikkan</span>
                </span>
                <span v-if="r.note" class="mt-1 block break-words text-xs"
                  :class="r.done ? 'text-slate-400 line-through' : 'text-slate-600'">{{ r.note }}</span>
              </span>

              <button class="shrink-0 rounded-md p-1 text-slate-300 hover:bg-slate-100 hover:text-rose-500"
                aria-label="O'chirish" @click="leadRemindersApi.remove(r.id)">
                <AppIcon name="trash" class="h-3.5 w-3.5" />
              </button>
            </li>
          </ul>
          <p v-else-if="!showReminderForm" class="mt-2.5 text-xs text-slate-400">Bu lead uchun eslatma yo'q.</p>

          <h3 class="mb-3 mt-5 text-sm font-semibold text-slate-900">Faoliyat tarixi</h3>
          <ol class="relative space-y-4 border-l border-slate-200 pl-4">
            <li v-for="(h, i) in detailHistory" :key="i" class="relative">
              <span class="absolute -left-[22px] top-1 h-2.5 w-2.5 rounded-full ring-4 ring-white"
                :class="h.color || 'bg-slate-300'" />
              <div class="flex items-start justify-between gap-2">
                <p class="text-[13px] font-medium text-slate-800">{{ h.title }}</p>
                <p class="shrink-0 text-[11px] text-slate-400">{{ h.author }}</p>
              </div>
              <p class="text-[11px] text-slate-400">{{ h.date }}</p>
              <p v-if="h.text" class="mt-1 text-xs text-slate-600">{{ h.text }}</p>
            </li>
          </ol>
        </div>
      </aside>
    </Transition>

    <!-- Modal -->
    <ModalDialog :open="modalOpen" :title="form.id ? 'Leadni tahrirlash' : 'Yangi lead qo\'shish'"
      @close="modalOpen = false" @submit="save">
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="1. Ism Familiya">
          <input v-model="form.name" class="field" placeholder="Ism Familiya kiriting" />
        </FormField>

        <FormField label="2. Telefon raqam">
          <PhoneInput v-model="form.phone" />
        </FormField>

        <FormField label="3. Qaysi tur">
          <select v-model="form.tour" class="field">
            <option value="">Turni tanlang</option>
            <option v-for="t in db.tours" :key="t.id" :value="t.name">{{ t.name }}</option>
          </select>
        </FormField>

        <FormField label="4. Nechta odam">
          <input v-model="form.people" type="number" min="1" class="field" placeholder="Masalan: 2" />
        </FormField>

        <FormField label="5. Summa (USD)" hint="Masalan: 1850">
          <input v-model="form.amount" type="number" min="0" step="10" class="field" placeholder="1850" />
        </FormField>

        <FormField v-if="isSuperAdmin" label="6. Mas'ul menejer">
          <select v-model="form.manager" class="field">
            <option value="">Tanlanmagan</option>
            <option v-for="e in db.employees" :key="e.id" :value="e.name">{{ e.name }}</option>
          </select>
        </FormField>

        <FormField label="7. Manba">
          <select v-model="form.source" class="field">
            <option v-for="s in leadSourceNames" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>

        <FormField label="8. Bosqich">
          <select v-model="form.stage" class="field">
            <option v-for="s in leadStages" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>

        <FormField label="9. Telegram username" hint="Ixtiyoriy. Bo'sh bo'lsa telefon raqami ishlatiladi">
          <input v-model="form.telegram" class="field" placeholder="@username" />
        </FormField>

        <FormField label="10. Shahar">
          <input v-model="form.city" class="field" placeholder="Toshkent" />
        </FormField>
      </div>

      <div class="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="11. Kommentariya" class="sm:col-span-2">
          <textarea v-model="form.comment" rows="3" class="field resize-y"
            placeholder="Izoh yoki qo'shimcha ma'lumot kiriting..." />
        </FormField>

        <FormField label="12. Sana" hint="Sana avtomatik qo'yiladi">
          <input v-model="form.date" class="field" placeholder="DD.MM.YYYY" />
        </FormField>
      </div>
    </ModalDialog>

    <ConfirmDialog :open="!!toDelete" title="Leadni o'chirish"
      :message="`${toDelete?.name} ro'yxatdan o'chiriladi. Bu amalni qaytarib bo'lmaydi.`" @cancel="toDelete = null"
      @confirm="confirmDelete" />
  </div>
</template>