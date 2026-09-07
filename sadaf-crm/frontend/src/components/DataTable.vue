<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, required: true }
})
</script>
<template>
  <div class="card overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full min-w-[640px] text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50/70 text-left text-xs uppercase tracking-wide text-slate-500">
            <th v-for="c in columns" :key="c.key" class="px-5 py-3 font-medium"
                :class="c.align === 'right' ? 'text-right' : ''">
              {{ c.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in rows" :key="i" class="border-b border-slate-50 last:border-0 hover:bg-slate-50/60">
            <td v-for="c in columns" :key="c.key" class="px-5 py-3.5"
                :class="c.align === 'right' ? 'text-right' : ''">
              <slot :name="c.key" :row="row">
                <span :class="c.key === 'name' ? 'font-medium text-slate-900' : 'text-slate-600'">{{ row[c.key] }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
