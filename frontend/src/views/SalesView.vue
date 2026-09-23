<script setup>
import { ref, computed } from 'vue'
import MetricTile from '@/components/MetricTile.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import SourceTag from '@/components/SourceTag.vue'
import ToolbarButton from '@/components/ToolbarButton.vue'
import TablePagination from '@/components/TablePagination.vue'
import AppIcon from '@/components/AppIcon.vue'
import { db } from '@/store'
import { money, exportCsv } from '@/utils/format.js'

// Savdolar leadlar bosqichidan AVTOMATIK hosil bo'ladi:
// lead "To'lov qilindi" yoki "Bron tasdiqlandi" bo'lganda backend
// sales.json ga yozuv qo'shadi. Bosqich orqaga qaytsa — yozuv o'chadi.

const PER_PAGE = 10
const page = ref(1)
const query = ref('')
const managerFilter = ref('')

const managers = computed(() =>
  [...new Set(db.sales.map((s) => s.manager).filter(Boolean))].sort()
)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  return db.sales.filter((s) =>
    (!q || String(s.client).toLowerCase().includes(q) || String(s.tour).toLowerCase().includes(q)) &&
    (!managerFilter.value || s.manager === managerFilter.value)
  )
})

const paged = computed(() =>
  filtered.value.slice((page.value - 1) * PER_PAGE, page.value * PER_PAGE)
)

const metrics = computed(() => {
  const rows = filtered.value
  const total = rows.reduce((s, r) => s + Number(r.amount || 0), 0)
  const people = rows.reduce((s, r) => s + Number(r.people || 0), 0)
  return {
    count: rows.length,
    total: money(total),
    avg: money(rows.length ? Math.round(total / rows.length) : 0),
    people,
    managers: new Set(rows.map((r) => r.manager).filter(Boolean)).size
  }
})

const exportColumns = [
  { key: 'client', label: 'Mijoz' }, { key: 'phone', label: 'Telefon' },
  { key: 'tour', label: 'Tur' }, { key: 'people', label: 'Odam' },
  { key: 'amount', label: 'Summa (USD)' }, { key: 'manager', label: 'Menejer' },
  { key: 'source', label: 'Manba' }, { key: 'date', label: 'Sana' }
]
</script>

<template>
  <div class="space-y-5">
    <div class="stagger grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <MetricTile label="Jami savdolar" :value="metrics.count" unit="ta" icon="handshake" color="blue" />
      <MetricTile label="Umumiy tushum" :value="metrics.total" icon="dollar" color="green" />
      <MetricTile label="O'rtacha chek" :value="metrics.avg" icon="chart" color="violet" />
      <MetricTile label="Sayohatchilar" :value="metrics.people" unit="kishi" icon="users" color="amber" />
      <MetricTile label="Faol menejerlar" :value="metrics.managers" unit="nafar" icon="user" color="teal" />
    </div>

    <div class="card overflow-hidden">
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 px-5 py-4">
        <div class="relative min-w-[220px] flex-1 sm:max-w-xs">
          <AppIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input v-model="query" type="search" class="field pl-9"
                 placeholder="Mijoz yoki tur bo'yicha qidirish" @input="page = 1" />
        </div>

        <select v-model="managerFilter" class="field w-auto min-w-[170px]" @change="page = 1">
          <option value="">Barcha menejerlar</option>
          <option v-for="m in managers" :key="m" :value="m">{{ m }}</option>
        </select>

        <div class="ml-auto">
          <ToolbarButton icon="download" @click="exportCsv('savdolar.csv', exportColumns, filtered)">
            Export
          </ToolbarButton>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px] text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50/70 text-left text-xs uppercase tracking-wide text-slate-500">
              <th class="px-5 py-3 font-medium">Mijoz</th>
              <th class="px-5 py-3 font-medium">Tur</th>
              <th class="px-5 py-3 text-right font-medium">Odam</th>
              <th class="px-5 py-3 text-right font-medium">Summa</th>
              <th class="px-5 py-3 font-medium">Menejer</th>
              <th class="px-5 py-3 font-medium">Manba</th>
              <th class="px-5 py-3 font-medium">Sana</th>
              <th class="px-5 py-3 font-medium">Bosqich</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in paged" :key="s.id" class="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
              <td class="px-5 py-3.5">
                <span class="block font-medium text-slate-900">{{ s.client }}</span>
                <span class="block text-xs text-slate-400">{{ s.phone }}</span>
              </td>
              <td class="px-5 py-3.5 text-slate-600">{{ s.tour || '—' }}</td>
              <td class="px-5 py-3.5 text-right text-slate-600">{{ s.people || '—' }}</td>
              <td class="px-5 py-3.5 text-right font-semibold text-slate-900">{{ money(s.amount) }}</td>
              <td class="px-5 py-3.5 text-slate-600">{{ s.manager || '—' }}</td>
              <td class="px-5 py-3.5"><SourceTag v-if="s.source" :source="s.source" /><span v-else>—</span></td>
              <td class="px-5 py-3.5 text-slate-600">{{ s.date }}</td>
              <td class="px-5 py-3.5"><StatusBadge v-if="s.stage" :status="s.stage" /></td>
            </tr>

            <tr v-if="!paged.length">
              <td colspan="8" class="px-5 py-12 text-center text-sm text-slate-500">
                Hozircha savdo yo'q. Lead "To'lov qilindi" yoki "Bron tasdiqlandi"
                bosqichiga o'tganda bu yerda paydo bo'ladi.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <TablePagination v-model:page="page" :total="filtered.length" :per-page="PER_PAGE"
                       :summary="`Jami ${filtered.length} ta savdo`" />
    </div>
  </div>
</template>
