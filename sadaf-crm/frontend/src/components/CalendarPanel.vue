<script setup>
import { ref, computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { db } from '@/store'

const MONTHS = ['Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
                'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr']
const WEEKDAYS = ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya']

const nowDate = new Date()
const cursor = ref(new Date(nowDate.getFullYear(), nowDate.getMonth(), 1))
const selected = ref(
  `${String(nowDate.getDate()).padStart(2, '0')}.` +
  `${String(nowDate.getMonth() + 1).padStart(2, '0')}.${nowDate.getFullYear()}`
)

const pad = (n) => String(n).padStart(2, '0')
const key = (y, m, d) => `${pad(d)}.${pad(m + 1)}.${y}`
const label = computed(() => `${MONTHS[cursor.value.getMonth()]} ${cursor.value.getFullYear()}`)
const days = computed(() => {
  const y = cursor.value.getFullYear()
  const m = cursor.value.getMonth()
  const first = new Date(y, m, 1)
  const offset = (first.getDay() + 6) % 7 
  const count = new Date(y, m + 1, 0).getDate()

  const out = []
  for (let i = 0; i < offset; i++) out.push(null)
  for (let d = 1; d <= count; d++) out.push({ d, key: key(y, m, d) })
  return out
})
const eventsFor = (k) => {
  if (!k) return []
  const items = []
  db.tasks.filter((t) => t.due === k).forEach((t) =>
    items.push({ kind: 'task', title: t.title, meta: t.to, time: t.time, done: t.done }))
  db.leads.filter((l) => l.date === k).forEach((l) =>
    items.push({ kind: 'lead', title: l.name, meta: l.tour, time: l.stage }))
  return items
}
const selectedEvents = computed(() => eventsFor(selected.value))
const move = (step) => {
  const c = cursor.value
  cursor.value = new Date(c.getFullYear(), c.getMonth() + step, 1)
}
const today = key(new Date().getFullYear(), new Date().getMonth(), new Date().getDate())
</script>
<template>
  <div> ball
    <div class="flex items-center justify-between px-4 py-3">
      <button class="grid h-8 w-8 place-items-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50"
              aria-label="Oldingi oy" @click="move(-1)">
        <AppIcon name="chevron" class="h-4 w-4 rotate-90" />
      </button>
      <p class="text-sm font-semibold text-slate-900">{{ label }}</p>
      <button class="grid h-8 w-8 place-items-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50"
              aria-label="Keyingi oy" @click="move(1)">
        <AppIcon name="chevron" class="h-4 w-4 -rotate-90" />
      </button>
    </div>
    <div class="grid grid-cols-7 px-3 text-center text-[11px] font-medium text-slate-400">
      <span v-for="w in WEEKDAYS" :key="w" class="py-1">{{ w }}</span>
    </div>
    <div class="grid grid-cols-7 gap-1 px-3 pb-3">
      <template v-for="(cell, i) in days" :key="i">
        <span v-if="!cell" />
        <button v-else
                class="relative grid h-9 place-items-center rounded-lg text-sm transition"
                :class="[
                  selected === cell.key ? 'bg-blue-600 font-semibold text-white'
                  : today === cell.key ? 'bg-blue-50 font-semibold text-blue-700'
                  : 'text-slate-700 hover:bg-slate-100'
                ]"
                @click="selected = cell.key">
          {{ cell.d }}
          <span v-if="eventsFor(cell.key).length"
                class="absolute bottom-1 h-1 w-1 rounded-full"
                :class="selected === cell.key ? 'bg-white' : 'bg-brand-orange'" />
        </button>
      </template>
    </div>
    <div class="max-h-64 overflow-y-auto border-t border-slate-100 bg-slate-50/60 px-4 py-3">
      <p class="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">{{ selected }}</p>

      <ul v-if="selectedEvents.length" class="space-y-2">
        <li v-for="(e, i) in selectedEvents" :key="i"
            class="flex items-start gap-2.5 rounded-xl bg-white p-2.5 shadow-sm">
          <span class="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg"
                :class="e.kind === 'task' ? 'bg-violet-50 text-violet-600' : 'bg-sky-50 text-sky-600'">
            <AppIcon :name="e.kind === 'task' ? 'check-square' : 'send'" class="h-3.5 w-3.5" />
          </span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm text-slate-800" :class="e.done ? 'line-through text-slate-400' : ''">
              {{ e.title }}
            </span>
            <span class="block truncate text-xs text-slate-400">{{ e.meta }}</span>
          </span>
          <span class="shrink-0 text-xs text-slate-400">{{ e.time }}</span>
        </li>
      </ul>

      <p v-else class="py-4 text-center text-sm text-slate-400">Bu kunda hodisa yo'q.</p>
    </div>
  </div>
</template>
