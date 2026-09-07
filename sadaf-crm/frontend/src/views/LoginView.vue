<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppIcon from '@/components/AppIcon.vue'
import BrandLogo from '@/components/BrandLogo.vue'
import { signIn as authSignIn, ui } from '@/store'

const router = useRouter()
const login = ref('')
const password = ref('')
const showPassword = ref(false)
const remember = ref(true)
const error = ref('')
const busy = ref(false)
const aboutOpen = ref(false)

async function signIn() {
  if (busy.value) return
  if (!login.value.trim() || !password.value.trim()) {
    error.value = 'Login va parolni kiriting.'
    return
  }

  busy.value = true
  error.value = ''
  try {
    const ok = await authSignIn(login.value.trim(), password.value)
    if (!ok) {
      error.value = ui.error || "Login yoki parol noto'g'ri. Qaytadan urinib ko'ring."
      return
    }
    router.push('/dashboard')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="relative min-h-screen overflow-hidden bg-[#f4f4f8]">
    <!-- ——— Butun ekranni qopl aydigan umumiy fon rasmi ——— -->
    <img
      src="/login-bg.jpg"
      alt=""
      aria-hidden="true"
      class="pointer-events-none fixed inset-0 h-full w-full object-cover"
    />

    <!-- ——— CHAP: Santorini fonli navy panel + egri chekka ——— -->
    <div class="enter-panel absolute inset-y-0 left-0 hidden w-[58%] lg:block" aria-hidden="true">
      <!-- Rasm: brightness/saturate bilan yoritilgan -->
      <div class="absolute inset-0 bg-cover bg-center"
           style="background-image: url('/login-bg.jpg'); clip-path: url(#curveClip);
                  filter: brightness(1.25) saturate(1.1)" />
      <!-- Qoplama: tepa/past qorong'iroq, o'rta ochiq — logo o'qilishi uchun -->
      <div class="absolute inset-0 bg-gradient-to-t from-navy-900/80 via-navy-900/35 to-navy-900/55"
           style="clip-path: url(#curveClip)" />

      <svg class="absolute inset-0 h-full w-full" viewBox="0 0 800 1000" preserveAspectRatio="none">
        <defs>
          <clipPath id="curveClip" clipPathUnits="objectBoundingBox">
            <path d="M0 0 H0.83 C0.95 0.26 0.75 0.42 0.83 0.62 C0.89 0.8 0.78 0.9 0.70 1 H0 Z" />
          </clipPath>
        </defs>
        <!-- oltin chekka chizig'i -->
        <path d="M664 0 C760 260 600 420 664 620 C712 800 624 900 560 1000"
              fill="none" stroke="#e0a06a" stroke-width="2.5" opacity=".9" />
        <!-- pastki dekorativ to'lqinlar -->
        <g fill="none" stroke="#e0a06a" stroke-width="1.5" opacity=".35">
          <path d="M0 880 C120 840 240 900 380 862" />
          <path d="M0 920 C130 878 250 940 400 900" />
          <path d="M0 960 C140 918 260 978 420 938" />
        </g>
      </svg>

      <div class="relative flex h-full w-[80%] flex-col items-center justify-center px-10 text-center">
        <BrandLogo size="h-56 xl:h-64" variant="light" class="enter-left drop-shadow-2xl" />
        <p class="enter-left delay-2 mt-6 text-lg font-light tracking-wide text-white/90 drop-shadow-lg">
          Sayohatlaringizni biz bilan boshlang
        </p>
      </div>
    </div>

    <!-- ——— Mobil sarlavha ——— -->
    <div class="relative flex flex-col items-center bg-navy-900 px-6 py-10 lg:hidden">
      <div class="absolute inset-0 bg-cover bg-center opacity-45" style="background-image: url('/login-bg.jpg')" />
      <BrandLogo size="h-28 sm:h-36" variant="light" class="enter-left relative" />
    </div>

    <!-- ——— O'NG: kirish kartasi ——— -->
    <div class="relative mx-auto flex min-h-[70vh] max-w-[1500px] items-center justify-center px-6 py-10 lg:min-h-screen lg:justify-end lg:px-16">
      <div class="enter-right w-full max-w-[420px] rounded-3xl bg-white p-7 shadow-2xl shadow-navy-900/20 sm:p-9">

        <h2 class="enter-right delay-3 mt-5 text-center text-2xl font-bold text-navy-900">Hisobingizga kiring</h2>
        <p class="enter-right delay-4 mt-1.5 text-center text-sm text-slate-500">
          Davom etish uchun login va parolingizni kiriting
        </p>

        <div class="enter-right delay-4 mt-6 space-y-4">
          <div>
            <label for="login" class="mb-1.5 block text-sm font-medium text-slate-700">Login</label>
            <div class="relative">
              <AppIcon name="user" class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input id="login" v-model="login" type="text" class="field pl-10"
                     placeholder="Loginni kiriting" autocomplete="username" @keyup.enter="signIn" />
            </div>
          </div>

          <div>
            <label for="password" class="mb-1.5 block text-sm font-medium text-slate-700">Parol</label>
            <div class="relative">
              <AppIcon name="lock" class="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'"
                     class="field px-10" placeholder="Parolni kiriting"
                     autocomplete="current-password" @keyup.enter="signIn" />
              <button type="button"
                      class="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                      :aria-label="showPassword ? 'Parolni yashirish' : 'Parolni ko\'rsatish'"
                      @click="showPassword = !showPassword">
                <AppIcon :name="showPassword ? 'eye' : 'eye-off'" class="h-4 w-4" />
              </button>
            </div>
          </div>

          <p v-if="error" class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{{ error }}</p>

          <button class="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-navy-900 to-[#1e3a6d] py-3.5 text-sm font-semibold text-white shadow-lg shadow-navy-900/25 transition hover:brightness-110 disabled:opacity-60"
                  :disabled="busy" @click="signIn">
            <AppIcon :name="busy ? 'refresh' : 'arrow-right'" class="h-4 w-4" :class="busy && 'animate-spin'" />
            {{ busy ? 'Tekshirilmoqda...' : 'Kirish' }}
          </button>
        </div>
        <div v-if="aboutOpen" class="animate-fade-up mt-3 space-y-1.5 rounded-xl bg-slate-50 p-4 text-xs leading-relaxed text-slate-600">
          <p><b>SADAF CRM</b> — turagentlik uchun leadlar, mijozlar, turlar va hodimlarni boshqarish tizimi.</p>
          <p>Boshlang'ich kirish: login <b>admin</b>, parol <b>admin123</b>.</p>
          <p>Hodimlar uchun login va parolni administrator "Hodimlar" bo'limida yaratadi.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ——— Kirish animatsiyalari ———
   Chap panel va logo chapdan, kirish kartasi o'ngdan sirg'alib chiqadi. */

@keyframes enterLeft {
  from { opacity: 0; transform: translateX(-56px); }
  to   { opacity: 1; transform: none; }
}
@keyframes enterRight {
  from { opacity: 0; transform: translateX(56px); }
  to   { opacity: 1; transform: none; }
}
@keyframes enterUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: none; }
}
@keyframes enterPop {
  from { opacity: 0; transform: scale(.7); }
  to   { opacity: 1; transform: none; }
}
@keyframes enterPanel {
  from { opacity: 0; transform: translateX(-100%); }
  to   { opacity: 1; transform: none; }
}

.enter-left  { animation: enterLeft  .7s cubic-bezier(.22, .9, .3, 1) both; }
.enter-right { animation: enterRight .7s cubic-bezier(.22, .9, .3, 1) both; }
.enter-up    { animation: enterUp    .6s ease both; }
.enter-pop   { animation: enterPop   .5s cubic-bezier(.34, 1.56, .64, 1) both; }
.enter-panel { animation: enterPanel .9s cubic-bezier(.22, .9, .3, 1) both; }

/* Ketma-ket chiqishi uchun kechikishlar */
.delay-2 { animation-delay: .18s; }
.delay-3 { animation-delay: .26s; }
.delay-4 { animation-delay: .36s; }
.delay-5 { animation-delay: .46s; }
.delay-6 { animation-delay: .56s; }

/* Animatsiyani kamaytirish yoqilgan bo'lsa — darhol ko'rsatamiz */
@media (prefers-reduced-motion: reduce) {
  .enter-left, .enter-right, .enter-up, .enter-pop, .enter-panel {
    animation: none;
  }
}
</style>