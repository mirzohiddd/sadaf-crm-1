<script setup>
// Lead kommentariyalari (formadagi 11-bo'lim va detal paneli).
//
// - Lead hali saqlanmagan bo'lsa (id yo'q): faqat matn maydoni ko'rsatiladi,
//   yozilgan matn (v-model) lead yaratilganda birinchi kommentariya bo'ladi.
// - Mavjud leadda: kommentariyalar tarixi (sana/vaqt bilan) + yangisini
//   qo'shish. "Saqlash" darhol serverga yozadi — lead formasini saqlash shart emas.
import { ref, computed, nextTick, watch } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { auth, isSuperAdmin, leadComments, leadCommentsApi } from '@/store'

const props = defineProps({
  lead: { type: Object, default: null },
  // Yozish maydoni boshidan ochiq tursinmi (modalda — ha, panelda — yo'q)
  startOpen: { type: Boolean, default: false },
  // Panel uchun ixchamroq ko'rinish
  compact: { type: Boolean, default: false }
})

const draft = defineModel({ type: String, default: '' })

const isSaved = computed(() => props.lead?.id != null)
const items = computed(() => leadComments(props.lead))

const open = ref(props.startOpen)
const saving = ref(false)
const error = ref('')
const listEl = ref(null)
const inputEl = ref(null)

// Boshqa lead ochilganda holat tozalanadi
watch(() => props.lead?.id, () => {
  open.value = props.startOpen
  error.value = ''
})

function canDelete(c) {
  if (c.id === 'legacy') return false
  return isSuperAdmin.value || (c.authorId != null && c.authorId === auth.user?.id)
}

async function toggleOpen() {
  open.value = !open.value
  error.value = ''
  if (open.value) {
    await nextTick()
    inputEl.value?.focus()
  }
}

async function submit() {
  const text = draft.value.trim()
  if (!text) {
    error.value = 'Kommentariya matnini yozing.'
    return
  }
  error.value = ''
  saving.value = true
  const res = await leadCommentsApi.add(props.lead.id, text)
  saving.value = false
  if (!res.ok) {
    error.value = res.message || "Saqlab bo'lmadi. Qaytadan urinib ko'ring."
    return
  }
  draft.value = ''
  if (!props.startOpen) open.value = false
  await nextTick()
  if (listEl.value) listEl.value.scrollTop = listEl.value.scrollHeight
}

// Ctrl/Cmd + Enter — tezkor saqlash
function onKeydown(e) {
  if (isSaved.value && e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    submit()
  }
}

function remove(c) {
  if (window.confirm("Kommentariya o'chirilsinmi?")) leadCommentsApi.remove(props.lead.id, c.id)
}

// Lead modalidagi umumiy "Saqlash" bosilganda yozilib qolgan matn
// yo'qolmasligi uchun tashqaridan chaqiriladi.
async function flush() {
  if (isSaved.value && draft.value.trim()) await submit()
}
defineExpose({ flush })
</script>

<template>
  <div>
    <!-- Yangi lead: faqat matn maydoni -->
    <template v-if="!isSaved">
      <textarea v-model="draft" rows="3" class="field resize-y" placeholder="Yangi kommentariya yozing..." />
      <p class="mt-1 text-xs text-slate-400">Lead saqlanganda sana va vaqt bilan birinchi kommentariya bo'lib qo'shiladi.</p>
    </template>

    <template v-else>
      <!-- Tarix -->
      <ul v-if="items.length" ref="listEl" class="space-y-2 overflow-y-auto pr-0.5"
        :class="compact ? 'max-h-72' : 'max-h-64'">
        <li v-for="c in items" :key="c.id"
          class="group rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 shadow-sm">
          <p class="whitespace-pre-line break-words text-sm text-slate-800">{{ c.text }}</p>
          <div class="mt-1.5 flex items-center gap-1.5 text-[11px] text-slate-400">
            <AppIcon name="clock" class="h-3 w-3 shrink-0" />
            <span class="tabular-nums">{{ c.date }}</span>
            <template v-if="c.author"><span>·</span><span class="truncate">{{ c.author }}</span></template>
            <button v-if="canDelete(c)" type="button"
              class="ml-auto rounded-md p-0.5 text-slate-300 opacity-0 transition hover:bg-rose-50 hover:text-rose-500 focus:opacity-100 group-hover:opacity-100"
              aria-label="Kommentariyani o'chirish" @click="remove(c)">
              <AppIcon name="trash" class="h-3.5 w-3.5" />
            </button>
          </div>
        </li>
      </ul>
      <p v-else-if="!open" class="text-xs text-slate-400">Hali kommentariya yo'q.</p>

      <!-- Qo'shish -->
      <button type="button"
        class="mt-2.5 inline-flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm font-medium text-blue-600 hover:bg-blue-50"
        @click="toggleOpen">
        <AppIcon :name="open ? 'close' : 'plus'" class="h-4 w-4" />
        {{ open ? 'Yopish' : "Kommentariya qo'shish" }}
      </button>

      <div v-if="open" class="mt-2 space-y-2">
        <textarea ref="inputEl" v-model="draft" rows="3" class="field resize-y bg-white"
          placeholder="Yangi kommentariya yozing..." @keydown="onKeydown" />
        <p v-if="error" class="text-xs text-rose-600">{{ error }}</p>
        <div class="flex items-center justify-end gap-3">
          <span class="hidden text-[11px] text-slate-400 sm:inline">Ctrl + Enter</span>
          <button type="button"
            class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
            :disabled="saving || !draft.trim()" @click="submit">
            {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
