<script setup>
import { ref, computed, reactive } from 'vue'
import MetricTile from '@/components/MetricTile.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import FormField from '@/components/FormField.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import SourceTag from '@/components/SourceTag.vue'
import ToolbarButton from '@/components/ToolbarButton.vue'
import TablePagination from '@/components/TablePagination.vue'
import AppIcon from '@/components/AppIcon.vue'
import { db, clientsApi } from '@/store'
import { countries, countryFlags, leadSourceNames, clientStatuses } from '@/data/mock.js'
import { money, exportCsv } from '@/utils/format.js'

const PER_PAGE = 6
const page = ref(1)
const query = ref('')
const countryFilter = ref('')
const sourceFilter = ref('')
const statusFilter = ref('')
const openMenu = ref(null)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return db.clients.filter((c) =>
    (!q || c.name.toLowerCase().includes(q) || c.phone.includes(q)) &&
    (!countryFilter.value || c.country === countryFilter.value) &&
    (!sourceFilter.value || c.source === sourceFilter.value) &&
    (!statusFilter.value || c.status === statusFilter.value)
  )
})

const paged = computed(() => filtered.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE))

const metrics = computed(() => {
  const all = db.clients
  const active = all.filter((c) => c.status === 'Faol').length
  const travelled = all.filter((c) => c.trips > 0).length
  const total = all.reduce((s, c) => s + Number(c.total || 0), 0)
  const pct = (n) => (all.length ? ((n / all.length) * 100).toFixed(1) + '%' : '0%')
  return {
    total: all.length,
    active, activePct: pct(active),
    travelled, travelledPct: pct(travelled),
    spend: money(total),
    avg: money(all.length ? Math.round(total / all.length) : 0),
    loyal: all.filter((c) => c.trips >= 3).length,
    loyalPct: pct(all.filter((c) => c.trips >= 3).length),
    fresh: all.filter((c) => c.status === 'Yangi').length,
    noTrip: all.filter((c) => c.trips === 0).length,
    noTripPct: pct(all.filter((c) => c.trips === 0).length),
    repeat: all.filter((c) => c.trips >= 2).length,
    repeatPct: pct(all.filter((c) => c.trips >= 2).length),
    potential: money(all.filter((c) => c.status !== 'Sovuq').length * 1450)
  }
})

// ——— Modal ———

const emptyForm = () => ({ id: null, name: '', phone: '', country: '', source: 'Telegram', lastDate: '', lastTour: '', trips: 0, total: 0, status: 'Yangi', manager: '', vip: false })

const modalOpen = ref(false)
const form = reactive(emptyForm())
const errors = reactive({})
const clearErrors = () => Object.keys(errors).forEach((k) => delete errors[k])

function openCreate() {
  Object.assign(form, emptyForm())
  clearErrors()
  modalOpen.value = true
}

function openEdit(row) {
  Object.assign(form, { ...row })
  clearErrors()
  openMenu.value = null
  modalOpen.value = true
}

function validate() {
  clearErrors()
  if (!form.name.trim()) errors.name = 'Ism familiyani kiriting.'
  if (!/^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$/.test(form.phone.trim()))
    errors.phone = "Telefonni +998 XX XXX XX XX ko'rinishida kiriting."
  if (!form.country) errors.country = 'Mamlakatni tanlang.'
  return !Object.keys(errors).length
}

function save() {
  if (!validate()) return
  const payload = { ...form, trips: Number(form.trips), total: Number(form.total), lastTour: form.lastTour || form.country }
  form.id ? clientsApi.update(payload) : clientsApi.add(payload)
  modalOpen.value = false
}

const toDelete = ref(null)

function confirmDelete() {
  clientsApi.remove(toDelete.value.id)
  toDelete.value = null
  const maxPage = Math.max(1, Math.ceil(filtered.value.length / PER_PAGE))
  if (page.value > maxPage) page.value = maxPage
}

const exportColumns = [
  { key: 'name', label: 'Mijoz' }, { key: 'phone', label: 'Telefon' },
  { key: 'country', label: 'Mamlakat' }, { key: 'source', label: 'Manba' },
  { key: 'lastDate', label: 'Oxirgi sayohat' }, { key: 'trips', label: 'Sayohatlar' },
  { key: 'total', label: 'Jami xarajat' }, { key: 'status', label: 'Status' }
]
</script>

<template>
  <div class="space-y-5" @click="openMenu = null">
    <!-- Yuqori ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <MetricTile label="Jami mijozlar" :value="metrics.total" note="barcha vaqt" icon="users" color="blue" />
      <MetricTile label="Faol mijozlar" :value="metrics.active" :note="metrics.activePct" icon="bag" color="green" />
      <MetricTile label="Sayohat qilganlar" :value="metrics.travelled" :note="metrics.travelledPct" icon="plane" color="violet" />
      <MetricTile label="Jami xarajat" :value="metrics.spend" note="barcha vaqt" icon="dollar" color="amber" />
      <MetricTile label="O'rtacha xarajat" :value="metrics.avg" note="bir mijozga" icon="chart" color="teal" />
    </div>

    <div class="card overflow-hidden">
      <!-- Filtrlar -->
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 px-5 py-4">
        <div class="relative min-w-[220px] flex-1 sm:max-w-xs">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input v-model="query" type="search" class="field pl-9" placeholder="Ism yoki telefon bo'yicha qidirish..." @input="page = 1" />
        </div>

        <select v-model="countryFilter" class="field w-auto min-w-[160px]" @change="page = 1">
          <option value="">Barcha mamlakatlar</option>
          <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
        </select>

        <select v-model="sourceFilter" class="field w-auto min-w-[150px]" @change="page = 1">
          <option value="">Barcha manbalar</option>
          <option v-for="s in leadSourceNames" :key="s" :value="s">{{ s }}</option>
        </select>

        <select v-model="statusFilter" class="field w-auto min-w-[150px]" @change="page = 1">
          <option value="">Barcha holatlar</option>
          <option v-for="s in clientStatuses" :key="s" :value="s">{{ s }}</option>
        </select>

        <div class="ml-auto flex gap-3">
          <ToolbarButton icon="download" @click="exportCsv('mijozlar.csv', exportColumns, filtered)">Export</ToolbarButton>
          <ToolbarButton icon="plus" variant="primary" @click="openCreate">Yangi mijoz</ToolbarButton>
        </div>
      </div>

      <!-- Jadval -->
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1020px] text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/70 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="px-5 py-3 font-medium">Mijoz</th>
              <th class="px-5 py-3 font-medium">Telefon</th>
              <th class="px-5 py-3 font-medium">Mamlakat</th>
              <th class="px-5 py-3 font-medium">Manba</th>
              <th class="px-5 py-3 font-medium">Oxirgi sayohat</th>
              <th class="px-5 py-3 text-right font-medium">Sayohatlar</th>
              <th class="px-5 py-3 text-right font-medium">Jami xarajat</th>
              <th class="px-5 py-3 font-medium">Status</th>
              <th class="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in paged" :key="c.id" class="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <UserAvatar :name="c.name" />
                  <span>
                    <span class="block font-medium text-slate-900">{{ c.name }}</span>
                    <span class="mt-0.5 flex gap-1.5">
                      <span v-if="c.vip" class="badge bg-amber-50 text-amber-700">VIP</span>
                      <StatusBadge :status="c.status" />
                    </span>
                  </span>
                </div>
              </td>
              <td class="px-5 py-3.5 text-slate-600">{{ c.phone }}</td>
              <td class="px-5 py-3.5 text-slate-600">{{ countryFlags[c.country] }} {{ c.country }}</td>
              <td class="px-5 py-3.5"><SourceTag :source="c.source" /></td>
              <td class="px-5 py-3.5">
                <span class="block text-slate-600">{{ c.lastDate || '—' }}</span>
                <span class="block text-xs text-slate-400">{{ c.lastTour || '—' }}</span>
              </td>
              <td class="px-5 py-3.5 text-right text-slate-600">{{ c.trips }}</td>
              <td class="px-5 py-3.5 text-right font-semibold text-slate-900">{{ money(c.total) }}</td>
              <td class="px-5 py-3.5"><StatusBadge :status="c.status" /></td>
              <td class="px-5 py-3.5 text-right">
                <div class="relative inline-block">
                  <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                          aria-label="Amallar" @click.stop="openMenu = openMenu === c.id ? null : c.id">
                    <AppIcon name="dots" class="h-4 w-4" />
                  </button>

                  <div v-if="openMenu === c.id"
                       class="absolute right-0 z-10 mt-1 w-44 rounded-xl border border-slate-100 bg-white py-1.5 text-left shadow-xl"
                       @click.stop>
                    <button class="block w-full px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                            @click="openEdit(c)">Tahrirlash</button>
                    <button class="block w-full px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                            @click="clientsApi.update({ id: c.id, vip: !c.vip }); openMenu = null">
                      {{ c.vip ? 'VIP belgisini olish' : 'VIP qilish' }}
                    </button>
                    <button class="block w-full border-t border-slate-100 px-4 py-2 text-sm text-rose-600 hover:bg-rose-50"
                            @click="toDelete = c; openMenu = null">O'chirish</button>
                  </div>
                </div>
              </td>
            </tr>

            <tr v-if="!paged.length">
              <td colspan="9" class="px-5 py-12 text-center text-sm text-slate-500">
                Mijoz topilmadi. Filtrlarni tozalang yoki yangi mijoz qo'shing.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination v-model:page="page" :total="filtered.length" :per-page="PER_PAGE"
                       :summary="`Jami ${filtered.length} ta mijoz`" />
    </div>

    <!-- Pastki ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <MetricTile label="Sodiq mijozlar" :value="metrics.loyal" :note="metrics.loyalPct" icon="star" color="amber" />
      <MetricTile label="Yangi mijozlar" :value="metrics.fresh" note="oxirgi 30 kun" note-tone="up" icon="clock" color="violet" />
      <MetricTile label="Sayohatsiz mijozlar" :value="metrics.noTrip" :note="metrics.noTripPct" note-tone="warn" icon="bag" color="rose" />
      <MetricTile label="Potensial daromad" :value="metrics.potential" note="kelgusi 30 kun" icon="dollar" color="green" />
      <MetricTile label="Takroriy mijozlar" :value="metrics.repeat" :note="metrics.repeatPct" icon="refresh" color="sky" />
    </div>

    <!-- Modal -->
    <ModalDialog :open="modalOpen" :title="form.id ? 'Mijozni tahrirlash' : 'Yangi mijoz qo\'shish'"
                 @close="modalOpen = false" @submit="save">
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="Ism Familiya" required :error="errors.name">
          <input v-model="form.name" class="field" placeholder="Ism Familiya kiriting" />
        </FormField>

        <FormField label="Telefon raqam" required :error="errors.phone">
          <PhoneInput v-model="form.phone" />
        </FormField>

        <FormField label="Mamlakat" required :error="errors.country">
          <select v-model="form.country" class="field">
            <option value="" disabled>Mamlakatni tanlang</option>
            <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
          </select>
        </FormField>

        <FormField label="Manba" required>
          <select v-model="form.source" class="field">
            <option v-for="s in leadSourceNames" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>

        <FormField label="Oxirgi sayohat sanasi">
          <input v-model="form.lastDate" class="field" placeholder="DD.MM.YYYY" />
        </FormField>

        <FormField label="Mas'ul menejer">
          <select v-model="form.manager" class="field">
            <option value="">Tanlanmagan</option>
            <option v-for="e in db.employees" :key="e.id" :value="e.name">{{ e.name }}</option>
          </select>
        </FormField>

        <FormField label="Status">
          <select v-model="form.status" class="field">
            <option v-for="s in clientStatuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>

        <FormField label="Sayohatlar soni">
          <input v-model="form.trips" type="number" min="0" class="field" placeholder="0" />
        </FormField>

        <FormField label="Jami xarajat (USD)">
          <input v-model="form.total" type="number" min="0" class="field" placeholder="0" />
        </FormField>

        <label class="flex items-center gap-2 text-sm text-slate-700 sm:col-span-2">
          <input v-model="form.vip" type="checkbox" class="h-4 w-4 accent-amber-500" /> VIP mijoz
        </label>
      </div>
    </ModalDialog>

    <ConfirmDialog :open="!!toDelete" title="Mijozni o'chirish"
                   :message="`${toDelete?.name} bazadan o'chiriladi. Bu amalni qaytarib bo'lmaydi.`"
                   @cancel="toDelete = null" @confirm="confirmDelete" />
  </div>
</template>
