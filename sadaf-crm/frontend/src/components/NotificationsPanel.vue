<script setup>
import { computed } from 'vue'
import AppIcon from './AppIcon.vue'
import { db, notificationsApi } from '@/store'
import { money } from '@/utils/format.js'

const items = computed(() => db.notifications)
const unread = computed(() => items.value.filter((n) => !n.read).length)

// Oy bo'yicha umumiy balans (kirim - chiqim)
const balance = computed(() => items.value.reduce((s, n) => s + Number(n.amount || 0), 0))
</script>

<template>
  <div>
    <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
      <h2 class="text-sm font-semibold text-slate-900">
        Bildirishnomalar
        <span v-if="unread" class="ml-1 text-xs font-normal text-slate-400">({{ unread }} yangi)</span>
      </h2>

      <span class="rounded-full px-2.5 py-1 text-xs font-semibold"
            :class="balance >= 0 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'">
        {{ balance >= 0 ? '+' : '' }}{{ money(balance) }}
      </span>
    </div>

    <ul v-if="items.length" class="max-h-[380px] divide-y divide-slate-50 overflow-y-auto">
      <li v-for="n in items" :key="n.id"
          class="flex items-center gap-3 px-4 py-3 transition hover:bg-slate-50"
          :class="n.read ? '' : 'bg-blue-50/40'"
          @click="notificationsApi.markRead(n.id)">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-full"
              :class="n.dir === 'up' ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'">
          <AppIcon name="chevron" class="h-4 w-4" :class="n.dir === 'up' ? 'rotate-180' : ''" />
        </span>

        <span class="min-w-0 flex-1">
          <span class="block truncate text-sm font-medium text-slate-900">{{ n.title }}</span>
          <span class="block truncate text-xs text-slate-400">{{ n.date }} · {{ n.detail }}</span>
        </span>

        <span v-if="n.amount" class="shrink-0 text-sm font-semibold"
              :class="n.amount > 0 ? 'text-emerald-600' : 'text-rose-600'">
          {{ n.amount > 0 ? '+' : '−' }}{{ money(Math.abs(n.amount)) }}
        </span>

        <button class="shrink-0 rounded-md p-1 text-slate-300 hover:bg-slate-100 hover:text-slate-500"
                aria-label="O'chirish" @click.stop="notificationsApi.remove(n.id)">
          <AppIcon name="close" class="h-3.5 w-3.5" />
        </button>
      </li>
    </ul>

    <p v-else class="px-4 py-10 text-center text-sm text-slate-400">Bildirishnoma yo'q.</p>

    <div v-if="items.length" class="border-t border-slate-100 px-4 py-2.5">
      <button class="w-full rounded-lg py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
              @click="notificationsApi.markAllRead()">
        Hammasini o'qilgan deb belgilash
      </button>
    </div>
  </div>
</template>
