<script setup>
import { ref, computed, reactive } from 'vue'
import MetricTile from '@/components/MetricTile.vue'
import ModalDialog from '@/components/ModalDialog.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import FormField from '@/components/FormField.vue'
import PhoneInput from '@/components/PhoneInput.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import RowActions from '@/components/RowActions.vue'
import ToolbarButton from '@/components/ToolbarButton.vue'
import TablePagination from '@/components/TablePagination.vue'
import AppIcon from '@/components/AppIcon.vue'
import { db, employeesApi, can } from '@/store'
import { workShifts, crmRoles, roleLabelOf } from '@/data/mock.js'
import { exportCsv } from '@/utils/format.js'

const PER_PAGE = 5
const page = ref(1)
const query = ref('')
const positionFilter = ref('')

// Lavozimlar ro'yxati endi statik emas — mavjud hodimlarning haqiqiy
// lavozimlaridan (Menejer 1, Menejer 2, ...) o'zi hosil bo'ladi.
const positionOptions = computed(() =>
  [...new Set(db.employees.map((e) => e.position).filter(Boolean))].sort()
)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return db.employees.filter((e) => {
    const okQuery = !q || e.name.toLowerCase().includes(q) || e.phone.includes(q)
    const okPosition = !positionFilter.value || e.position === positionFilter.value
    return okQuery && okPosition
  })
})

const paged = computed(() => filtered.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE))

const metrics = computed(() => {
  const all = db.employees
  return {
    total: all.length,
    working: all.filter((e) => e.status === 'Ishlayapti').length,
    vacation: all.filter((e) => e.status === "Ta'tilda").length,
    positions: new Set(all.map((e) => e.position)).size,
    deals: all.reduce((s, e) => s + Number(e.deals || 0), 0)
  }
})

// ——— Modal / forma ———

const emptyForm = () => ({
  id: null, name: '', phone: '', birthDate: '', hireDate: '',
  shift: '', status: 'Ishlayapti', position: '', address: '', deals: 0,
  crmLogin: '', crmPassword: '', crmRole: 'admin', managerId: null
})

const modalOpen = ref(false)
const form = reactive(emptyForm())
const errors = reactive({})

function clearErrors() {
  Object.keys(errors).forEach((k) => delete errors[k])
}

// Har bir yangi hodim uchun navbatdagi raqam bilan lavozim taklif qilinadi:
// Menejer 1, Menejer 2, Menejer 3 ... (hodimlar soniga qarab).
function suggestPosition() {
  return `Menejer ${db.employees.length + 1}`
}

function openCreate() {
  Object.assign(form, emptyForm())
  form.position = suggestPosition()
  clearErrors()
  modalOpen.value = true
}

function openEdit(row) {
  Object.assign(form, { ...row })
  clearErrors()
  modalOpen.value = true
}

function validate() {
  clearErrors()
  if (!form.name.trim()) errors.name = 'Ism familiyani kiriting.'
  if (!/^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$/.test(form.phone.trim()))
    errors.phone = "Telefonni +998 XX XXX XX XX ko'rinishida kiriting."
  if (!form.birthDate.trim()) errors.birthDate = "Tug'ilgan sanani kiriting."
  if (!form.hireDate.trim()) errors.hireDate = 'Ishga kirgan sanani kiriting.'
  if (!form.shift) errors.shift = 'Ish vaqtini tanlang.'
  if (!form.position.trim()) errors.position = 'Lavozimni kiriting.'
  if (!form.address.trim()) errors.address = 'Yashash manzilini kiriting.'
  if (!/^[a-z0-9._-]{3,}$/i.test(form.crmLogin.trim())) errors.crmLogin = "Login kamida 3 ta belgi (harf, raqam, . _ -) bo'lsin."
  else if (db.employees.some((e) => e.crmLogin === form.crmLogin.trim() && e.id !== form.id))
    errors.crmLogin = 'Bu login band. Boshqasini tanlang.'

  // Yangi hodimga parol shart; tahrirlashda bo'sh qoldirilsa eskisi saqlanadi
  const pwd = form.crmPassword.trim()
  if (!form.id && pwd.length < 6) errors.crmPassword = "Parol kamida 6 ta belgidan iborat bo'lsin."
  else if (form.id && pwd && pwd.length < 6) errors.crmPassword = "Parol kamida 6 ta belgidan iborat bo'lsin."
  return !Object.keys(errors).length
}

async function save() {
  if (!validate()) return
  const payload = { ...form, deals: Number(form.deals || 0) }

  // Bo'sh parol yuborilmaydi — backend eskisini o'zgartirmaydi
  if (form.id && !payload.crmPassword.trim()) delete payload.crmPassword

  const row = form.id ? await employeesApi.update(payload) : await employeesApi.add(payload)
  if (row) modalOpen.value = false
}

// Ism asosida login taklif qilish va tasodifiy parol yaratish
function suggestLogin() {
  const parts = form.name.trim().toLowerCase()
    .replace(/[^a-z\s']/g, '').split(/\s+/).filter(Boolean)
  if (!parts.length) return
  form.crmLogin = parts[0] + (parts[1] ? '.' + parts[1][0] : '')
}

function generatePassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789'
  let out = ''
  for (let i = 0; i < 10; i++) out += chars[Math.floor(Math.random() * chars.length)]
  form.crmPassword = out
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    // clipboard mavjud bo'lmasa jim o'tamiz
  }
}

// ——— O'chirish ———

const toDelete = ref(null)

async function confirmDelete() {
  await employeesApi.remove(toDelete.value.id)
  toDelete.value = null
  const maxPage = Math.max(1, Math.ceil(filtered.value.length / PER_PAGE))
  if (page.value > maxPage) page.value = maxPage
}

const exportColumns = [
  { key: 'name', label: 'Hodim' }, { key: 'position', label: 'Lavozim' },
  { key: 'phone', label: 'Telefon' }, { key: 'shift', label: 'Ish vaqti' },
  { key: 'hireDate', label: 'Ishga kirgan' }, { key: 'deals', label: 'Bitimlar' },
  { key: 'status', label: 'Holat' }, { key: 'address', label: 'Manzil' },
  { key: 'crmLogin', label: 'CRM login' }, { key: 'crmRoleLabel', label: 'CRM roli' }
]
</script>

<template>
  <div class="space-y-5">
    <!-- Yuqori ko'rsatkichlar -->
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <MetricTile label="Jami hodimlar" :value="metrics.total" unit="nafar" icon="users" color="blue" />
      <MetricTile label="Ishlayapti" :value="metrics.working" unit="nafar" icon="check-square" color="green" />
      <MetricTile label="Ta'tilda" :value="metrics.vacation" unit="nafar" icon="clock" color="amber" />
      <MetricTile label="Lavozimlar" :value="metrics.positions" unit="ta" icon="bag" color="violet" />
      <MetricTile label="Oylik bitimlar" :value="metrics.deals" unit="ta" note="Ushbu oy" icon="handshake" color="teal" />
    </div>

    <div class="card overflow-hidden">
      <!-- Asboblar paneli -->
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 px-5 py-4">
        <div class="relative min-w-[220px] flex-1 sm:max-w-xs">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input v-model="query" type="search" class="field pl-9" placeholder="Ism yoki telefon bo'yicha qidirish"
                 @input="page = 1" />
        </div>

        <select v-model="positionFilter" class="field w-auto min-w-[170px]" @change="page = 1">
          <option value="">Barcha lavozimlar</option>
          <option v-for="p in positionOptions" :key="p" :value="p">{{ p }}</option>
        </select>

        <div class="ml-auto flex gap-3">
          <ToolbarButton icon="download" @click="exportCsv('hodimlar.csv', exportColumns, filtered)">Export</ToolbarButton>
          <ToolbarButton v-if="can('employees', 'write')" icon="plus" variant="primary"
                         @click="openCreate">Yangi hodim</ToolbarButton>
        </div>
      </div>

      <!-- Jadval -->
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1180px] text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/70 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="px-5 py-3 font-medium">Hodim</th>
              <th class="px-5 py-3 font-medium">Telefon</th>
              <th class="px-5 py-3 font-medium">CRM login</th>
              <th class="px-5 py-3 font-medium">CRM parol</th>
              <th class="px-5 py-3 font-medium">Roli</th>
              <th class="px-5 py-3 font-medium">Ish vaqti</th>
              <th class="px-5 py-3 text-right font-medium">Bitimlar</th>
              <th class="px-5 py-3 font-medium">Holat</th>
              <th class="px-5 py-3 text-right font-medium">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in paged" :key="e.id" class="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-3">
                  <UserAvatar :name="e.name" />
                  <span>
                    <span class="block font-medium text-slate-900">{{ e.name }}</span>
                    <span class="block text-xs text-slate-500">{{ e.position }}</span>
                  </span>
                </div>
              </td>
              <td class="px-5 py-3.5 text-slate-600">{{ e.phone }}</td>

              <td class="px-5 py-3.5">
                <button class="group inline-flex items-center gap-1.5 rounded-lg bg-slate-50 px-2.5 py-1 font-mono text-xs text-slate-700 hover:bg-slate-100"
                        title="Nusxalash" @click="copyText(e.crmLogin)">
                  {{ e.crmLogin }}
                  <AppIcon name="copy" class="h-3.5 w-3.5 text-slate-400 group-hover:text-slate-600" />
                </button>
              </td>

              <td class="px-5 py-3.5">
                <!-- Parol backendda hash holida saqlanadi va hech qachon qaytarilmaydi.
                     O'zgartirish uchun tahrirlash oynasidan yangi parol kiritiladi. -->
                <span class="inline-flex items-center gap-1.5 text-xs text-slate-400">
                  <AppIcon name="lock" class="h-3.5 w-3.5" />
                  <span class="font-mono">••••••••</span>
                </span>
              </td>

              <td class="px-5 py-3.5">
                <span class="badge bg-indigo-50 text-indigo-700">{{ e.crmRoleLabel || roleLabelOf(e.crmRole) }}</span>
              </td>

              <td class="px-5 py-3.5 text-slate-600">{{ e.shift }}</td>
              <td class="px-5 py-3.5 text-right font-medium text-slate-800">{{ e.deals }}</td>
              <td class="px-5 py-3.5"><StatusBadge :status="e.status" /></td>
              <td class="px-5 py-3.5">
                <RowActions @edit="openEdit(e)" @remove="toDelete = e" />
              </td>
            </tr>

            <tr v-if="!paged.length">
              <td colspan="9" class="px-5 py-12 text-center text-sm text-slate-500">
                Hodim topilmadi. Qidiruvni tozalang yoki yangi hodim qo'shing.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination v-model:page="page" :total="filtered.length" :per-page="PER_PAGE"
                       :summary="`Jami ${filtered.length} ta hodim`" />
    </div>

    <!-- Yangi / tahrirlash oynasi -->
    <ModalDialog :open="modalOpen" :title="form.id ? 'Hodimni tahrirlash' : 'Yangi hodim qo\'shish'"
                 @close="modalOpen = false" @submit="save">
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
        <FormField label="1. Ism Familiya" required :error="errors.name">
          <input v-model="form.name" class="field" placeholder="Ism Familiya kiriting" />
        </FormField>

        <FormField label="5. Ish vaqti" required :error="errors.shift">
          <select v-model="form.shift" class="field">
            <option value="" disabled>Ish vaqtini tanlang</option>
            <option v-for="s in workShifts" :key="s" :value="s">{{ s }}</option>
          </select>
        </FormField>

        <FormField label="2. Telefon raqam" required :error="errors.phone">
          <PhoneInput v-model="form.phone" />
        </FormField>

        <FormField label="6. Holati" required>
          <div class="flex items-center gap-6 pt-2.5">
            <label class="flex items-center gap-2 text-sm text-slate-700">
              <input v-model="form.status" type="radio" value="Ishlayapti" class="h-4 w-4 accent-blue-600" /> Ishlayapti
            </label>
            <label class="flex items-center gap-2 text-sm text-slate-700">
              <input v-model="form.status" type="radio" value="Ta'tilda" class="h-4 w-4 accent-blue-600" /> Ta'tilda
            </label>
          </div>
        </FormField>

        <FormField label="3. Tug'ilgan sana" required :error="errors.birthDate">
          <input v-model="form.birthDate" class="field" placeholder="DD.MM.YYYY" />
        </FormField>

        <FormField label="7. Lavozim" required :error="errors.position"
                   hint="Avtomatik taklif qilinadi, xohlasangiz o'zgartirishingiz mumkin">
          <input v-model="form.position" class="field" placeholder="Masalan: Menejer 1" />
        </FormField>

        <FormField label="4. Ishga kirgan sana" required :error="errors.hireDate">
          <input v-model="form.hireDate" class="field" placeholder="DD.MM.YYYY" />
        </FormField>

        <FormField label="8. Yashash manzil" required :error="errors.address">
          <input v-model="form.address" class="field" placeholder="Yashash manzilini kiriting" />
        </FormField>
      </div>

      <!-- CRM hisobi -->
      <div class="mt-6 rounded-2xl border border-slate-100 bg-slate-50/70 p-5">
        <h3 class="text-sm font-semibold text-slate-900">CRM hisobi</h3>
        <p class="mt-0.5 text-xs text-slate-500">Hodim tizimga shu login va parol bilan kiradi.</p>

        <div class="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2">
          <FormField label="9. Login" required :error="errors.crmLogin">
            <div class="flex gap-2">
              <input v-model="form.crmLogin" class="field font-mono" placeholder="masalan: jasur.e" />
              <button class="shrink-0 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
                      title="Ismdan login yaratish" @click="suggestLogin">Taklif</button>
            </div>
          </FormField>

          <FormField label="10. Parol" :required="!form.id" :error="errors.crmPassword"
                     :hint="form.id ? 'Bo\'sh qoldirsangiz parol o\'zgarmaydi' : ''">
            <div class="flex gap-2">
              <input v-model="form.crmPassword" class="field font-mono"
                     :placeholder="form.id ? 'Yangi parol (ixtiyoriy)' : 'Kamida 6 ta belgi'" />
              <button class="shrink-0 rounded-xl border border-slate-200 bg-white px-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
                      title="Tasodifiy parol yaratish" @click="generatePassword">Yaratish</button>
            </div>
          </FormField>

          <FormField label="11. CRM roli" required class="sm:col-span-2">
            <select v-model="form.crmRole" class="field">
              <option v-for="r in crmRoles" :key="r.value" :value="r.value">{{ r.label }}</option>
            </select>
            <p class="mt-1.5 text-xs text-slate-400">
              Yangi hodim "Menejer" roli bilan qo'shiladi va Dashboard, Leadlar,
              Mijozlar, Savdolar, Hisobot va Sozlamalar bo'limlarini ko'radi.
            </p>
          </FormField>
        </div>
      </div>
    </ModalDialog>

    <ConfirmDialog :open="!!toDelete" title="Hodimni o'chirish"
                   :message="`${toDelete?.name} ro'yxatdan o'chiriladi. Bu amalni qaytarib bo'lmaydi.`"
                   @cancel="toDelete = null" @confirm="confirmDelete" />
  </div>
</template>