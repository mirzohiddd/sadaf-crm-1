<script setup>
import { ref, reactive } from 'vue'
import PanelCard from '@/components/PanelCard.vue'
import AppIcon from '@/components/AppIcon.vue'
import { auth, roleLabel } from '@/store'
import { authApi } from '@/api'

// Parol backendda PBKDF2 bilan hashlanadi. Frontend hech qachon
// hash'ni ko'rmaydi — faqat joriy va yangi parolni yuboradi.

const pwd = reactive({ current: '', next: '', repeat: '' })
const showCurrent = ref(false)
const busy = ref(false)
const message = reactive({ text: '', ok: false })

function say(text, ok = false) {
  Object.assign(message, { text, ok })
  if (ok) setTimeout(() => { message.text = '' }, 4000)
}

async function changePassword() {
  if (busy.value) return

  if (!pwd.current || !pwd.next || !pwd.repeat) return say("Barcha maydonlarni to'ldiring.")
  if (pwd.next.length < 6) return say("Yangi parol kamida 6 ta belgidan iborat bo'lsin.")
  if (pwd.next !== pwd.repeat) return say('Yangi parol tasdiqlash bilan mos kelmadi.')
  if (pwd.next === pwd.current) return say("Yangi parol eskisidan farq qilsin.")

  busy.value = true
  try {
    await authApi.changePassword(pwd.current, pwd.next)
    Object.assign(pwd, { current: '', next: '', repeat: '' })
    say('Parol yangilandi.', true)
  } catch (err) {
    say(err?.message || "Parolni o'zgartirib bo'lmadi.")
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <PanelCard title="Login va parol">
    <div class="max-w-xl space-y-4">
      <div>
        <label class="mb-1.5 block text-sm font-medium text-slate-700">Login</label>
        <input :value="auth.user?.login || ''" class="field bg-slate-50 font-mono" readonly />
        <p class="mt-1.5 text-xs text-slate-400">
          Roli: {{ roleLabel }}. Loginni faqat administrator o'zgartira oladi.
        </p>
      </div>

      <div>
        <label for="cur" class="mb-1.5 block text-sm font-medium text-slate-700">Joriy parol</label>
        <div class="relative">
          <input id="cur" v-model="pwd.current" :type="showCurrent ? 'text' : 'password'"
                 class="field pr-10" placeholder="••••••••" autocomplete="current-password" />
          <button type="button"
                  class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  :aria-label="showCurrent ? 'Yashirish' : 'Korsatish'"
                  @click="showCurrent = !showCurrent">
            <AppIcon :name="showCurrent ? 'eye' : 'eye-off'" class="h-4 w-4" />
          </button>
        </div>
      </div>

      <div>
        <label for="new" class="mb-1.5 block text-sm font-medium text-slate-700">Yangi parol</label>
        <input id="new" v-model="pwd.next" type="password" class="field" placeholder="••••••••"
               autocomplete="new-password" @keyup.enter="changePassword" />
      </div>

      <div>
        <label for="rep" class="mb-1.5 block text-sm font-medium text-slate-700">Yangi parolni tasdiqlang</label>
        <input id="rep" v-model="pwd.repeat" type="password" class="field" placeholder="••••••••"
               autocomplete="new-password" @keyup.enter="changePassword" />
      </div>

      <button class="btn-accent disabled:opacity-60" :disabled="busy" @click="changePassword">
        {{ busy ? 'Saqlanmoqda...' : 'Parolni yangilash' }}
      </button>

      <p v-if="message.text" class="text-sm" :class="message.ok ? 'text-emerald-600' : 'text-rose-600'">
        {{ message.text }}
      </p>
    </div>
  </PanelCard>
</template>
