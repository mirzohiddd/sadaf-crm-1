<script setup>
import { ref, computed, reactive } from 'vue'
import MetricTile from '@/components/MetricTile.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import FormField from '@/components/FormField.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import ToolbarButton from '@/components/ToolbarButton.vue'
import TablePagination from '@/components/TablePagination.vue'
import AppIcon from '@/components/AppIcon.vue'
import { db, toursApi } from '@/store'
import { countries, tourStatuses, countryFlags } from '@/data/mock.js'
import { money, exportCsv } from '@/utils/format.js'

const PER_PAGE = 6
const page = ref(1)
const query = ref('')
const countryFilter = ref('')
const statusFilter = ref('')

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return db.tours.filter((t) => {
    const okQuery = !q || t.name.toLowerCase().includes(q) || t.country.toLowerCase().includes(q)
    return okQuery &&
      (!countryFilter.value || t.country === countryFilter.value) &&
      (!statusFilter.value || t.status === statusFilter.value)
  })
})

const paged = computed(() => filtered.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE))

const metrics = computed(() => {
  const all = db.tours
  const seats = all.reduce((s, t) => s + Number(t.seats || 0), 0)
  const avg = all.length ? Math.round(all.reduce((s, t) => s + Number(t.price || 0), 0) / all.length) : 0
  const revenue = all.reduce((s, t) => s + Number(t.price || 0) * Number(t.seats || 0), 0)
  return { total: all.length, active: all.filter((t) => t.status === 'Faol').length, seats, avg, revenue }
})

// Har bir tur uchun barqaror rangli muqova (rasm o'rniga)
const covers = [
  'from-sky-400 to-blue-600', 'from-emerald-400 to-teal-600', 'from-amber-400 to-orange-600',
  'from-violet-400 to-purple-600', 'from-rose-400 to-pink-600', 'from-cyan-400 to-sky-600'
]
const cover = (name = '') => covers[[...name].reduce((s, c) => s + c.charCodeAt(0), 0) % covers.length]

// Bo'sh joy ko'rsatkichi uchun to'ldirish darajasi
const seatTone = (t) => (t.seats === 0 ? 'bg-rose-500' : t.seats <= 5 ? 'bg-amber-500' : 'bg-emerald-500')
const seatWidth = (t) => Math.min(100, (Number(t.seats) / 20) * 100) + '%'

// ——— Modal / forma ———

const emptyForm = () => ({ id: null, name: '', country: '', days: '', price: '', seats: '', status: '', description: '', image: '' })

const modalOpen = ref(false)
const form = reactive(emptyForm())
const errors = reactive({})
const imageName = ref('')

const clearErrors = () => Object.keys(errors).forEach((k) => delete errors[k])

function openCreate() {
  Object.assign(form, emptyForm())
  imageName.value = ''
  clearErrors()
  modalOpen.value = true
}

function openEdit(row) {
  Object.assign(form, { ...row })
  imageName.value = ''
  clearErrors()
  modalOpen.value = true
}

function onImagePick(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    errors.image = 'Faqat rasm fayli tanlang.'
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    errors.image = 'Fayl hajmi 2MB dan oshmasin.'
    return
  }
  delete errors.image
  imageName.value = file.name

  const reader = new FileReader()
  reader.onload = () => { form.image = String(reader.result) }
  reader.readAsDataURL(file)
}

function clearImage() {
  form.image = ''
  imageName.value = ''
}

function validate() {
  const keep = errors.image
  clearErrors()
  if (keep) errors.image = keep
  if (!form.name.trim()) errors.name = 'Tur nomini kiriting.'
  if (!form.country) errors.country = "Yo'nalishni tanlang."
  if (!(Number(form.days) > 0)) errors.days = 'Davomiylikni kun hisobida kiriting.'
  if (!(Number(form.price) > 0)) errors.price = 'Narxni kiriting.'
  if (form.seats === '' || Number(form.seats) < 0) errors.seats = "Bo'sh joylar sonini kiriting."
  if (!form.status) errors.status = 'Holatni tanlang.'
  return !Object.keys(errors).length
}

function save() {
  if (!validate()) return
  const payload = { ...form, days: Number(form.days), price: Number(form.price), seats: Number(form.seats) }
  form.id ? toursApi.update(payload) : toursApi.add(payload)
  modalOpen.value = false
}

// ——— Ko'rish va o'chirish ———

const viewing = ref(null)
const toDelete = ref(null)

function confirmDelete() {
  toursApi.remove(toDelete.value.id)
  toDelete.value = null
  const maxPage = Math.max(1, Math.ceil(filtered.value.length / PER_PAGE))
  if (page.value > maxPage) page.value = maxPage
}

const exportColumns = [
  { key: 'name', label: 'Tur nomi' }, { key: 'country', label: "Yo'nalish" },
  { key: 'days', label: 'Kun' }, { key: 'price', label: 'Narx (USD)' },
  { key: 'seats', label: "Bo'sh joy" }, { key: 'status', label: 'Holat' }
]
</script>

<template>
  <div class="space-y-5">
    <!-- Yuqori ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <MetricTile label="Jami turlar" :value="metrics.total" unit="ta" note="Barcha tur paketlari" icon="bag" color="blue" />
      <MetricTile label="Faol turlar" :value="metrics.active" unit="ta" note="Sotuvda" icon="plane" color="green" />
      <MetricTile label="Bo'sh joylar" :value="metrics.seats" unit="ta" note="Jami bo'sh joylar" icon="users" color="amber" />
      <MetricTile label="O'rtacha narx" :value="money(metrics.avg)" note="Bir tur uchun" icon="dollar" color="violet" />
      <MetricTile label="Potensial daromad" :value="money(metrics.revenue)" note="Barcha joylar sotilsa" icon="chart" color="teal" />
    </div>

    <!-- Asboblar paneli -->
    <div class="card flex flex-wrap items-center gap-3 p-4">
      <div class="relative min-w-[220px] flex-1 sm:max-w-xs">
        <AppIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input v-model="query" type="search" class="field pl-9" placeholder="Tur yoki yo'nalish bo'yicha qidirish" @input="page = 1" />
      </div>

      <select v-model="countryFilter" class="field w-auto min-w-[160px]" @change="page = 1">
        <option value="">Barcha yo'nalishlar</option>
        <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
      </select>

      <select v-model="statusFilter" class="field w-auto min-w-[150px]" @change="page = 1">
        <option value="">Barcha holatlar</option>
        <option v-for="s in tourStatuses" :key="s" :value="s">{{ s }}</option>
      </select>

      <div class="ml-auto flex gap-3">
        <ToolbarButton icon="download" @click="exportCsv('turlar.csv', exportColumns, filtered)">Export</ToolbarButton>
        <ToolbarButton icon="plus" variant="primary" @click="openCreate">Yangi tur</ToolbarButton>
      </div>
    </div>

    <!-- Turlar kartalari -->
    <div v-if="paged.length" class="stagger grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
      <article v-for="t in paged" :key="t.id" class="card lift group flex flex-col overflow-hidden">
        <!-- Muqova -->
        <div class="relative h-36 bg-gradient-to-br" :class="t.image ? '' : cover(t.name)">
          <img v-if="t.image" :src="t.image" :alt="t.name" class="h-full w-full object-cover" />
          <span v-else class="absolute inset-0 grid place-items-center text-white/40">
            <AppIcon name="globe" class="h-14 w-14" />
          </span>
          <span v-if="t.image" class="absolute inset-0 bg-gradient-to-t from-slate-900/50 to-transparent" />

          <span class="absolute left-3 top-3 rounded-lg bg-white/90 px-2.5 py-1 text-xs font-medium text-slate-700 backdrop-blur">
            {{ countryFlags[t.country] }} {{ t.country }}
          </span>

          <span class="absolute right-3 top-3">
            <StatusBadge :status="t.status" />
          </span>

          <span class="absolute bottom-3 right-3 rounded-lg bg-slate-900/70 px-2.5 py-1 text-sm font-semibold text-white backdrop-blur">
            {{ money(t.price) }}
          </span>
        </div>

        <!-- Matn qismi -->
        <div class="flex flex-1 flex-col p-5">
          <h3 class="text-base font-semibold text-slate-900">{{ t.name }}</h3>
          <p class="mt-1.5 line-clamp-2 text-sm text-slate-500">
            {{ t.description || 'Tavsif kiritilmagan.' }}
          </p>

          <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-xl bg-slate-50 px-3 py-2.5">
              <dt class="text-xs text-slate-500">Davomiyligi</dt>
              <dd class="mt-0.5 font-semibold text-slate-900">{{ t.days }} kun</dd>
            </div>
            <div class="rounded-xl bg-slate-50 px-3 py-2.5">
              <dt class="text-xs text-slate-500">Bo'sh joy</dt>
              <dd class="mt-0.5 font-semibold" :class="t.seats === 0 ? 'text-rose-600' : 'text-slate-900'">
                {{ t.seats }} ta
              </dd>
            </div>
          </dl>

          <!-- Joylar to'ldirilishi -->
          <div class="mt-4">
            <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
              <div class="h-full rounded-full" :class="seatTone(t)" :style="{ width: seatWidth(t) }" />
            </div>
            <p class="mt-1.5 text-xs text-slate-400">
              {{ t.seats === 0 ? "Joylar tugagan" : t.seats <= 5 ? "Joylar kam qoldi" : "Joylar yetarli" }}
            </p>
          </div>

          <!-- Amallar -->
          <div class="mt-5 flex gap-2 border-t border-slate-100 pt-4">
            <button class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-slate-50 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100"
                    @click="viewing = t">
              <AppIcon name="eye" class="h-4 w-4" /> Ko'rish
            </button>
            <button class="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 hover:bg-blue-100"
                    title="Tahrirlash" @click="openEdit(t)">
              <AppIcon name="pencil" class="h-4 w-4" />
            </button>
            <button class="grid h-10 w-10 place-items-center rounded-xl bg-rose-50 text-rose-600 hover:bg-rose-100"
                    title="O'chirish" @click="toDelete = t">
              <AppIcon name="trash" class="h-4 w-4" />
            </button>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="card p-12 text-center">
      <p class="text-sm text-slate-500">Tur topilmadi. Filtrlarni tozalang yoki yangi tur qo'shing.</p>
      <button class="mt-4 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
              @click="openCreate">Yangi tur qo'shish</button>
    </div>

    <div v-if="paged.length" class="card">
      <TablePagination v-model:page="page" :total="filtered.length" :per-page="PER_PAGE"
                       :summary="`Jami ${filtered.length} ta tur`" />
    </div>

    <!-- Yangi / tahrirlash -->
    <ModalDialog :open="modalOpen" :title="form.id ? 'Turni tahrirlash' : 'Yangi tur qo\'shish'"
                 @close="modalOpen = false" @submit="save">
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="Tur nomi" required :error="errors.name">
          <input v-model="form.name" class="field" placeholder="Masalan: Bangkok + Pattaya" />
        </FormField>

        <FormField label="Yo'nalish" required :error="errors.country">
          <select v-model="form.country" class="field">
            <option value="" disabled>Yo'nalishni tanlang</option>
            <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
          </select>
        </FormField>

        <FormField label="Davomiyligi (kun)" required :error="errors.days">
          <input v-model="form.days" type="number" min="1" class="field" placeholder="Masalan: 8" />
        </FormField>

        <FormField label="Narxi (USD)" required :error="errors.price">
          <input v-model="form.price" type="number" min="0" class="field" placeholder="Masalan: 1850" />
        </FormField>

        <FormField label="Bo'sh joylar soni" required :error="errors.seats">
          <input v-model="form.seats" type="number" min="0" class="field" placeholder="Masalan: 12" />
        </FormField>

        <FormField label="Holati" required :error="errors.status">
          <select v-model="form.status" class="field">
            <option value="" disabled>Holatni tanlang</option>
            <option v-for="s in tourStatuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>
      </div>

      <div class="mt-5 space-y-5">
        <FormField label="Tur tavsifi">
          <textarea v-model="form.description" rows="3" class="field resize-y"
                    placeholder="Tur haqida batafsil ma'lumot kiriting..." />
        </FormField>

        <FormField label="Rasm" :error="errors.image">
          <!-- Tanlangan rasm ko'rinishi -->
          <div v-if="form.image" class="relative overflow-hidden rounded-xl border border-slate-200">
            <img :src="form.image" alt="Tur rasmi" class="h-40 w-full object-cover" />
            <button class="absolute right-2 top-2 grid h-8 w-8 place-items-center rounded-lg bg-white/90 text-slate-600 shadow hover:bg-white"
                    title="Rasmni olib tashlash" @click="clearImage">
              <AppIcon name="close" class="h-4 w-4" />
            </button>
            <p v-if="imageName" class="truncate bg-slate-50 px-3 py-1.5 text-xs text-slate-500">{{ imageName }}</p>
          </div>

          <label v-else class="flex cursor-pointer flex-col items-center gap-1 rounded-xl border-2 border-dashed border-slate-200 py-7 text-center hover:border-blue-300 hover:bg-blue-50/40">
            <span class="flex items-center gap-2 text-sm font-medium text-slate-700">
              <AppIcon name="upload" class="h-4 w-4" /> Rasm yuklash
            </span>
            <span class="text-xs text-slate-400">JPG, PNG yoki WEBP (maks. 2MB)</span>
            <input type="file" accept="image/*" class="sr-only" @change="onImagePick" />
          </label>
        </FormField>
      </div>
    </ModalDialog>

    <!-- Ko'rish -->
    <ModalDialog :open="!!viewing" :title="viewing?.name || ''" @close="viewing = null" @submit="viewing = null">
      <div v-if="viewing" class="space-y-4">
        <div class="h-40 overflow-hidden rounded-xl">
          <img v-if="viewing.image" :src="viewing.image" :alt="viewing.name" class="h-full w-full object-cover" />
          <div v-else class="grid h-full place-items-center bg-gradient-to-br text-white/40" :class="cover(viewing.name)">
            <AppIcon name="globe" class="h-14 w-14" />
          </div>
        </div>
        <dl class="grid grid-cols-2 gap-4 text-sm">
          <div><dt class="text-slate-500">Yo'nalish</dt><dd class="font-medium text-slate-900">{{ countryFlags[viewing.country] }} {{ viewing.country }}</dd></div>
          <div><dt class="text-slate-500">Davomiyligi</dt><dd class="font-medium text-slate-900">{{ viewing.days }} kun</dd></div>
          <div><dt class="text-slate-500">Narxi</dt><dd class="font-medium text-slate-900">{{ money(viewing.price) }}</dd></div>
          <div><dt class="text-slate-500">Bo'sh joy</dt><dd class="font-medium text-slate-900">{{ viewing.seats }} ta</dd></div>
        </dl>
        <p class="text-sm text-slate-600">{{ viewing.description || 'Tavsif kiritilmagan.' }}</p>
      </div>
    </ModalDialog>

    <ConfirmDialog :open="!!toDelete" title="Turni o'chirish"
                   :message="`${toDelete?.name} ro'yxatdan o'chiriladi. Bu amalni qaytarib bo'lmaydi.`"
                   @cancel="toDelete = null" @confirm="confirmDelete" />
  </div>
</template>
