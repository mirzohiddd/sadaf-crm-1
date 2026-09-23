<script setup>
import { ref, onMounted, nextTick } from 'vue'
import AppIcon from './AppIcon.vue'
import { aiApi } from '@/api'
const input = ref('')
const thinking = ref(false)
const feed = ref(null)
const mode = ref('local')
const messages = ref([
  {
    role: 'ai',
    title: 'Salom!',
    lines: [
      "Men CRM yordamchisiman: leadlar, mijozlar, savdolar va vazifalar bo'yicha javob beraman.",
      'Oddiy suhbatga ham javob beraman. Masalan: "Bugun nechta lead keldi?", "Ali degan mijozni top".'
    ]
  }
])
const SUGGESTIONS = [
  'Bugun nechta lead keldi?',
  'Mening leadlarimni ko\'rsat',
  'Bu oy qancha savdo bo\'ldi?',
  'Bugungi vazifalarimni ko\'rsat'
]
onMounted(async () => {
  try {
    const status = await aiApi.status()
    mode.value = status.mode
  } catch {
    mode.value = 'local'
  }
})
async function scrollDown() {
  await nextTick()
  if (feed.value) feed.value.scrollTop = feed.value.scrollHeight
}
function historyPayload() {
  return messages.value
    .slice(-8)
    .map((m) => ({
      role: m.role === 'user' ? 'user' : 'ai',
      text: m.role === 'user' ? m.text : (m.text || (m.lines || []).join('\n'))
    }))
    .filter((m) => m.text)
}
async function ask(text) {
  const q = (text ?? input.value).trim()
  if (!q || thinking.value) return
  const history = historyPayload()
  messages.value.push({ role: 'user', text: q })
  input.value = ''
  thinking.value = true
  await scrollDown()
  try {
    const answer = await aiApi.chat(q, history)
    messages.value.push({
      role: 'ai',
      title: answer.title || null,
      lines: answer.lines?.length ? answer.lines : [answer.text || '—'],
      text: answer.text
    })
  } catch (err) {
    messages.value.push({
      role: 'ai',
      title: 'Xatolik',
      lines: [err?.message || "AI bilan bog'lanib bo'lmadi. Keyinroq urinib ko'ring."]
    })
  } finally {
    thinking.value = false
    await scrollDown()
  }
}
</script>
<template>
  <div class="flex h-[70vh] max-h-[460px] flex-col">
    <header class="flex items-center gap-2.5 border-b border-slate-100 px-4 py-3">
      <span class="grid h-8 w-8 place-items-center rounded-lg bg-blue-50 text-blue-600">
        <AppIcon name="bot" class="h-4 w-4" />
      </span>
      <span class="min-w-0 flex-1">
        <span class="block text-sm font-semibold text-slate-900">AI yordamchi</span>
        <span class="block truncate text-xs text-slate-400">
          {{ mode === 'anthropic' ? 'CRM ma\'lumotlari asosida' : 'Oflayn rejim (CRM ichida)' }}
        </span>
      </span>
    </header>
    <div ref="feed" class="flex-1 space-y-3 overflow-y-auto px-4 py-3">
      <template v-for="(m, i) in messages" :key="i">
        <div v-if="m.role === 'user'" class="flex justify-end">
          <p class="animate-fade-up max-w-[85%] rounded-2xl rounded-br-md bg-blue-600 px-3.5 py-2 text-sm text-white">
            {{ m.text }}
          </p>
        </div>
        <div v-else class="animate-fade-up max-w-[92%] rounded-2xl rounded-bl-md bg-slate-50 px-3.5 py-2.5">
          <p v-if="m.title" class="text-sm font-semibold text-slate-900">{{ m.title }}</p>
          <ul class="mt-1 space-y-1.5">
            <li v-for="(line, j) in m.lines" :key="j" class="flex gap-2 text-sm leading-relaxed text-slate-600">
              <span class="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-slate-300" />
              <span>{{ line }}</span>
            </li>
          </ul>
        </div>
      </template>
      <div v-if="messages.length === 1" class="flex flex-wrap gap-1.5 pt-1">
        <button v-for="s in SUGGESTIONS" :key="s"
                class="rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs text-slate-600 transition hover:bg-slate-50"
                @click="ask(s)">
          {{ s }}
        </button>
      </div>
      <div v-if="thinking" class="flex gap-1.5 rounded-2xl bg-slate-50 px-4 py-3">
        <span v-for="d in 3" :key="d" class="h-2 w-2 animate-bounce rounded-full bg-slate-300"
              :style="{ animationDelay: (d - 1) * 0.12 + 's' }" />
      </div>
    </div>

    <div class="flex items-center gap-2 border-t border-slate-100 p-3">
      <input v-model="input" class="field py-2.5 text-sm" placeholder="CRM haqida savol bering..."
             :disabled="thinking" @keyup.enter="ask()" />
      <button class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-blue-600 text-white transition hover:bg-blue-700 disabled:opacity-40"
              :disabled="!input.trim() || thinking" aria-label="Yuborish" @click="ask()">
        <AppIcon name="send" class="h-4 w-4" />
      </button>
    </div>
  </div>
</template>
