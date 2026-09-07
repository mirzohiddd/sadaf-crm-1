<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String })
const map = {
  'Tasdiqlandi': 'bg-emerald-50 text-emerald-700',
  "Mijoz bilan bog'lanilmadi": 'bg-amber-50 text-amber-700',
  "Bog'lanildi":      'bg-violet-50 text-violet-700',
  'Taklif yuborildi': 'bg-amber-50 text-amber-700',
  "To'lov qilindi":   'bg-sky-50 text-sky-700',
  'Bron tasdiqlandi': 'bg-emerald-50 text-emerald-700',
  'Bekor qilindi':    'bg-rose-50 text-rose-700',
  'Sifatsiz lead':    'bg-slate-100 text-slate-600',
  'Faol':        'bg-emerald-50 text-emerald-700',
  'Kutilmoqda':  'bg-slate-100 text-slate-600',
  'Yangi':       'bg-blue-50 text-blue-700',
  'Aloqada':     'bg-blue-50 text-blue-700',
  'Jarayonda':   'bg-amber-50 text-amber-700',
  'Muzokara':    'bg-amber-50 text-amber-700',
  'Taklif':      'bg-violet-50 text-violet-700',
  'Kam joy':     'bg-amber-50 text-amber-700',
  "Ta'tilda":    'bg-amber-50 text-amber-700',
  'Yopiq':       'bg-rose-50 text-rose-700'
}

const cls = computed(() => map[props.status] || 'bg-slate-100 text-slate-600')
</script>

<template>
  <span class="badge" :class="cls">{{ status }}</span>
</template>