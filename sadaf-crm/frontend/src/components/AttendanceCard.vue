<script setup>
import { computed, onMounted } from 'vue'
import AppIcon from './AppIcon.vue'
import { attendance, auth, checkIn, checkOut, loadAttendance } from '@/store'
onMounted(loadAttendance)
const record = computed(() => attendance.record)
const busy = computed(() => false)
const statusText = computed(() => {
  if (attendance.checkedIn) return `Ish boshlandi: ${record.value?.checkIn || '—'}`
  if (record.value?.checkOut) return `Yakunlandi: ${record.value.checkIn} — ${record.value.checkOut}`
  return 'Bugun hali ish boshlanmadi'
})
</script>
<template>
  <div class="card p-5">
    <div class="flex flex-wrap items-center gap-4">
      <span class="grid h-12 w-12 shrink-0 place-items-center rounded-xl text-white"
            :class="attendance.checkedIn ? 'bg-emerald-500' : 'bg-slate-400'">
        <AppIcon name="clock" class="h-6 w-6" />
      </span>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-semibold text-slate-900">Ish vaqti</p>
        <p class="text-xs text-slate-500">{{ statusText }}</p>
      </div>
      <dl class="flex gap-6 border-slate-100 sm:border-l sm:pl-6">
        <div>
          <dt class="text-xs text-slate-400">Bu oy</dt>
          <dd class="text-sm font-semibold text-slate-900">{{ attendance.hours }} soat</dd>
        </div>
        <div>
          <dt class="text-xs text-slate-400">Kunlar</dt>
          <dd class="text-sm font-semibold text-slate-900">{{ attendance.days }} ta</dd>
        </div>
        <div class="hidden sm:block">
          <dt class="text-xs text-slate-400">O'rtacha</dt>
          <dd class="text-sm font-semibold text-slate-900">{{ attendance.avgHours }} soat</dd>
        </div>
      </dl>
      <button v-if="!attendance.checkedIn"
              class="flex items-center gap-2 rounded-xl bg-emerald-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-600 disabled:opacity-50"
              :disabled="busy" @click="checkIn">
        <AppIcon name="check-circle" class="h-4 w-4" /> Check in
      </button>
      <button v-else
              class="flex items-center gap-2 rounded-xl bg-rose-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-rose-600 disabled:opacity-50"
              :disabled="busy" @click="checkOut">
        <AppIcon name="logout" class="h-4 w-4" /> Check out
      </button>
    </div>
  </div>
</template>
