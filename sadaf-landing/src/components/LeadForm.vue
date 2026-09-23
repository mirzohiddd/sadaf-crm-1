<script setup>
import { reactive, ref } from 'vue'
import { submitLead } from '../services/api'

const destinations = [
  'Turkiya — Antalya',
  'BAA — Dubay',
  'Gretsiya — Santorini',
  'Maldiv orollari',
  'Misr — Sharm el-Shayx',
  'Gruziya — Batumi',
  'Boshqa yo‘nalish'
]

const form = reactive({
  name: '',
  phone: '',
  destination: '',
  travelDate: '',
})

const errors = reactive({
  name: '',
  phone: '',
  destination: '',
  travelDate: '',
})

const status = ref('idle') // idle | loading | success | error
const errorMessage = ref('')

const PHONE_PATTERN = /^\+?\d[\d\s-]{8,14}\d$/

function todayISO() {
  return new Date().toISOString().split('T')[0]
}

function validate() {
  errors.name = form.name.trim().length >= 2 ? '' : 'Ismingizni to‘liq kiriting'
  errors.phone = PHONE_PATTERN.test(form.phone.trim())
    ? ''
    : 'Telefon raqamini to‘g‘ri kiriting'
  errors.destination = form.destination ? '' : 'Yo‘nalishni tanlang'
  errors.travelDate = form.travelDate ? '' : 'Sanani tanlang'

  return Object.values(errors).every((message) => message === '')
}

function formatPhoneInput(event) {
  form.phone = event.target.value
  if (errors.phone) errors.phone = ''
}

async function handleSubmit() {
  if (status.value === 'loading') return

  if (!validate()) {
    status.value = 'idle'
    return
  }

  status.value = 'loading'
  errorMessage.value = ''

  try {
    await submitLead({
      name: form.name.trim(),
      phone: form.phone.trim(),
      destination: form.destination,
      travelDate: form.travelDate
    })
    status.value = 'success'
    form.name = ''
    form.phone = ''
    form.destination = ''
    form.travelDate = ''
    form.consent = false
  } catch (error) {
    status.value = 'error'
    errorMessage.value =
      error?.message || 'Nimadir xato ketdi. Iltimos, birozdan so‘ng qayta urinib ko‘ring.'
  }
}

function resetToIdle() {
  status.value = 'idle'
}
</script>

<template>
  <div class="rounded-[28px] bg-pearl-100 p-6 shadow-card sm:p-8">
    <!-- Success state -->
    <div v-if="status === 'success'" class="flex flex-col items-center py-6 text-center">
      <div class="flex h-16 w-16 items-center justify-center rounded-full bg-nacre-500/15">
        <svg class="h-8 w-8 text-nacre-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20 6 9 17l-5-5" />
        </svg>
      </div>
      <h3 class="mt-5 font-display text-2xl text-navy-900">Arizangiz qabul qilindi!</h3>
      <p class="mt-2 max-w-xs text-sm text-navy-900/70">
        Tez orada mutaxassisimiz siz bilan bog‘lanadi va sayohatingizni birga rejalashtiramiz.
      </p>
      <button
        type="button"
        class="mt-6 text-sm font-semibold text-nacre-600 underline-offset-4 hover:underline"
        @click="resetToIdle"
      >
        Yana bitta ariza yuborish
      </button>
    </div>

    <!-- Form -->
    <form v-else novalidate class="space-y-5" @submit.prevent="handleSubmit">
      <div>
        <h3 class="font-display text-2xl text-navy-900 sm:text-[1.7rem]">Ariza qoldiring</h3>
        <p class="mt-1.5 text-sm leading-relaxed text-navy-900/60">
          Sayohatingizni rejalashtirish uchun bizga quyidagi ma’lumotlarni yuboring
        </p>
      </div>

      <!-- Name -->
      <div>
        <label for="name" class="mb-1.5 block text-sm font-semibold text-navy-900">
          Ismingiz
        </label>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-900/35" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M12 12a4.5 4.5 0 1 0 0-9 4.5 4.5 0 0 0 0 9Z" />
            <path d="M4.5 20.5a7.5 7.5 0 0 1 15 0" />
          </svg>
          <input
            id="name"
            v-model="form.name"
            type="text"
            autocomplete="name"
            placeholder="Ismingizni kiriting"
            class="w-full rounded-xl border bg-white py-3 pl-10 pr-3.5 text-[0.95rem] text-navy-900 placeholder:text-navy-900/35 focus:border-nacre-500 focus:outline-none"
            :class="errors.name ? 'border-coral-500' : 'border-navy-900/12'"
            @blur="errors.name = form.name.trim().length >= 2 ? '' : 'Ismingizni to‘liq kiriting'"
          />
        </div>
        <p v-if="errors.name" class="mt-1.5 text-xs font-medium text-coral-600">{{ errors.name }}</p>
      </div>

      <!-- Phone -->
      <div>
        <label for="phone" class="mb-1.5 block text-sm font-semibold text-navy-900">
          Telefon raqamingiz
        </label>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-900/35" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M4 5.5c0-.6.4-1 1-1h2.4c.5 0 .9.3 1 .8l.8 3.3c.1.4 0 .9-.4 1.2l-1.4 1.2a12 12 0 0 0 5.6 5.6l1.2-1.4c.3-.3.7-.5 1.2-.4l3.3.8c.5.1.8.5.8 1V19c0 .6-.4 1-1 1h-1.5C9.9 20 4 14.1 4 7V5.5Z" />
          </svg>
          <input
            id="phone"
            :value="form.phone"
            type="tel"
            inputmode="tel"
            autocomplete="tel"
            placeholder="+998 90 123 45 67"
            class="w-full rounded-xl border bg-white py-3 pl-10 pr-3.5 text-[0.95rem] text-navy-900 placeholder:text-navy-900/35 focus:border-nacre-500 focus:outline-none"
            :class="errors.phone ? 'border-coral-500' : 'border-navy-900/12'"
            @input="formatPhoneInput"
            @blur="errors.phone = PHONE_PATTERN.test(form.phone.trim()) ? '' : 'Telefon raqamini to‘g‘ri kiriting'"
          />
        </div>
        <p v-if="errors.phone" class="mt-1.5 text-xs font-medium text-coral-600">{{ errors.phone }}</p>
      </div>

      <!-- Destination -->
      <div>
        <label for="destination" class="mb-1.5 block text-sm font-semibold text-navy-900">
          Qayerga ketmoqchisiz?
        </label>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-900/35" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21Z" />
            <circle cx="12" cy="9.5" r="2.3" />
          </svg>
          <select
            id="destination"
            v-model="form.destination"
            class="w-full appearance-none rounded-xl border bg-white py-3 pl-10 pr-9 text-[0.95rem] focus:border-nacre-500 focus:outline-none"
            :class="form.destination ? 'text-navy-900' : 'text-navy-900/35'"
            :aria-invalid="!!errors.destination"
            @change="errors.destination = form.destination ? '' : 'Yo‘nalishni tanlang'"
          >
            <option value="" disabled selected>Yo‘nalishni tanlang</option>
            <option v-for="d in destinations" :key="d" :value="d">{{ d }}</option>
          </select>
          <svg class="pointer-events-none absolute right-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-900/40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
        <p v-if="errors.destination" class="mt-1.5 text-xs font-medium text-coral-600">{{ errors.destination }}</p>
      </div>

      <!-- Date -->
      <div>
        <label for="travelDate" class="mb-1.5 block text-sm font-semibold text-navy-900">
          Qachon yo‘l olishni rejalashtiryapsiz?
        </label>
        <div class="relative">
          <svg class="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-900/35" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <rect x="3.5" y="5" width="17" height="15.5" rx="2" />
            <path d="M3.5 9.5h17M8 3v3.5M16 3v3.5" />
          </svg>
          <input
            id="travelDate"
            v-model="form.travelDate"
            type="date"
            :min="todayISO()"
            class="w-full rounded-xl border bg-white py-3 pl-10 pr-3.5 text-[0.95rem] text-navy-900 focus:border-nacre-500 focus:outline-none"
            :class="errors.travelDate ? 'border-coral-500' : 'border-navy-900/12'"
            @blur="errors.travelDate = form.travelDate ? '' : 'Sanani tanlang'"
          />
        </div>
        <p v-if="errors.travelDate" class="mt-1.5 text-xs font-medium text-coral-600">{{ errors.travelDate }}</p>
      </div>



      <!-- Server error -->
      <p v-if="status === 'error'" class="rounded-xl bg-coral-500/10 px-3.5 py-2.5 text-xs font-medium text-coral-600">
        {{ errorMessage }}
      </p>

      <!-- Submit -->
      <button
        type="submit"
        :disabled="status === 'loading'"
        class="flex w-full items-center justify-center gap-2.5 rounded-full bg-coral-500 py-3.5 text-sm font-bold tracking-wide text-pearl-100 transition-colors hover:bg-coral-600 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <svg v-if="status === 'loading'" class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle class="opacity-25" cx="12" cy="12" r="9" stroke="currentColor" stroke-width="3" />
          <path class="opacity-90" d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
        </svg>
        <svg v-else class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M2.5 12 21 3l-5 18-6-6.5L2.5 12Z" />
        </svg>
        {{ status === 'loading' ? 'Yuborilmoqda...' : 'ARIZA YUBORISH' }}
      </button>

    </form>
  </div>
</template>
