<script setup>
import SadafLogo from './SadafLogo.vue'
import LeadForm from './LeadForm.vue'
import heroImage from '../assets/hero-santorini.png'

const highlights = [
  {
    text: 'Dunyoning istalgan nuqtasiga sayohat',
    icon: 'globe'
  },
  {
    text: 'Ishonchli va xavfsiz xizmat',
    icon: 'shield'
  },
  {
    text: '24/7 qo‘llab-quvvatlash',
    icon: 'support'
  }
]
</script>

<template>
  <section class="relative overflow-hidden bg-navy-900">
    <!-- Background photo -->
    <div class="absolute inset-0">
      <img
        :src="heroImage"
        alt=""
        aria-hidden="true"
        class="h-full w-full object-cover"
        loading="eager"
      />
      <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-navy-900"></div>
      <div class="absolute inset-0 bg-gradient-to-r from-navy-900/70 via-navy-900/25 to-transparent"></div>
    </div>

    <div class="container-page relative py-6 sm:py-9">
      <!-- Top row: logo + badge -->
      <div class="flex flex-wrap items-center justify-between gap-4">
        <SadafLogo />
        <div class="flex items-center gap-2 rounded-full bg-navy-900/55 px-4 py-2 ring-1 ring-inset ring-nacre-400/40 backdrop-blur-sm">
          <svg class="h-4 w-4 shrink-0 text-nacre-400" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M2.5 12 21 3l-5 18-6-6.5L2.5 12Z" />
          </svg>
          <span class="text-xs font-semibold text-pearl-100 sm:text-sm">
            Sizning orzudagi sayohatingiz biz bilan boshlanadi!
          </span>
        </div>
      </div>

      <!-- Main hero grid -->
      <div class="mt-10 grid gap-10 pb-14 sm:mt-14 sm:pb-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-start lg:gap-14">
        <div class="lg:pt-6">
          <h1 class="font-display text-[2.6rem] leading-[1.05] text-pearl-100 [text-shadow:0_2px_20px_rgba(15,17,40,0.85)] sm:text-6xl lg:text-[3.6rem]">
            Dunyo sizni<br />kutmoqda!
          </h1>
          <p class="mt-5 max-w-md text-[0.98rem] leading-relaxed text-pearl-100/90 [text-shadow:0_1px_12px_rgba(15,17,40,0.9)] sm:text-base">
            Eng yaxshi yo‘nalishlar va qulay narxlar bilan sayohatingizni bizga ishonib topshiring.
          </p>

          <ul class="mt-8 space-y-4">
            <li v-for="item in highlights" :key="item.text" class="flex items-center gap-3.5">
              <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-navy-900/55 ring-1 ring-inset ring-nacre-400/40 backdrop-blur-sm">
                <svg v-if="item.icon === 'globe'" class="h-[18px] w-[18px] text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                  <circle cx="12" cy="12" r="8.5" />
                  <path d="M12 3.5c2.5 2.4 3.8 5.3 3.8 8.5s-1.3 6.1-3.8 8.5c-2.5-2.4-3.8-5.3-3.8-8.5S9.5 5.9 12 3.5Z" />
                  <path d="M3.8 9.5h16.4M3.8 14.5h16.4" />
                </svg>
                <svg v-else-if="item.icon === 'shield'" class="h-[18px] w-[18px] text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                  <path d="M12 3.5 19 6.5v5.3c0 4.5-3 7.9-7 8.7-4-.8-7-4.2-7-8.7V6.5L12 3.5Z" />
                  <path d="m9 12 2 2 4-4" />
                </svg>
                <svg v-else class="h-[18px] w-[18px] text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
                  <path d="M4 13.5v-2a8 8 0 0 1 16 0v2" />
                  <rect x="2.5" y="13" width="4.5" height="6" rx="1.4" />
                  <rect x="17" y="13" width="4.5" height="6" rx="1.4" />
                  <path d="M19.5 19.5A5.5 5.5 0 0 1 14 24" />
                </svg>
              </span>
              <span class="text-sm font-medium text-pearl-100 [text-shadow:0_1px_10px_rgba(15,17,40,0.9)] sm:text-[0.95rem]">{{ item.text }}</span>
            </li>
          </ul>
        </div>

        <div id="ariza-form">
          <LeadForm />
        </div>
      </div>
    </div>
  </section>
</template>
