<script setup>
import SadafLogo from './SadafLogo.vue'

const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="border-t border-pearl-100/10 bg-navy-900 py-12">
    <div class="container-page">
      <div class="grid gap-10 sm:grid-cols-3 sm:items-start">
        <div>
          <SadafLogo />
          <p class="mt-4 max-w-[220px] text-sm leading-relaxed text-pearl-100/50">
            Orzuingizdagi sayohatni biz bilan haqiqatga aylantiring.
          </p>
        </div>

        <div>
          <h4 class="text-sm font-bold text-pearl-100">Biz bilan bog‘laning</h4>
          <ul class="mt-4 space-y-3 text-sm text-pearl-100/60">
            <li class="flex items-center gap-2.5">
              <svg class="h-4 w-4 shrink-0 text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M4 5.5c0-.6.4-1 1-1h2.4c.5 0 .9.3 1 .8l.8 3.3c.1.4 0 .9-.4 1.2l-1.4 1.2a12 12 0 0 0 5.6 5.6l1.2-1.4c.3-.3.7-.5 1.2-.4l3.3.8c.5.1.8.5.8 1V19c0 .6-.4 1-1 1h-1.5C9.9 20 4 14.1 4 7V5.5Z" />
              </svg>
              <a href="tel:+998948148800" class="hover:text-pearl-100">+998 94 814 88 00</a>
            </li>
            <li class="flex items-center gap-2.5">
              <svg class="h-4 w-4 shrink-0 text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M4 5.5c0-.6.4-1 1-1h2.4c.5 0 .9.3 1 .8l.8 3.3c.1.4 0 .9-.4 1.2l-1.4 1.2a12 12 0 0 0 5.6 5.6l1.2-1.4c.3-.3.7-.5 1.2-.4l3.3.8c.5.1.8.5.8 1V19c0 .6-.4 1-1 1h-1.5C9.9 20 4 14.1 4 7V5.5Z" />
              </svg>
              <a href="tel:+998943148800" class="hover:text-pearl-100">+998 94 314 88 00</a>
            </li>
            <li class="flex items-center gap-2.5">
              <svg class="h-4 w-4 shrink-0 text-nacre-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M4 5.5c0-.6.4-1 1-1h2.4c.5 0 .9.3 1 .8l.8 3.3c.1.4 0 .9-.4 1.2l-1.4 1.2a12 12 0 0 0 5.6 5.6l1.2-1.4c.3-.3.7-.5 1.2-.4l3.3.8c.5.1.8.5.8 1V19c0 .6-.4 1-1 1h-1.5C9.9 20 4 14.1 4 7V5.5Z" />
              </svg>
              <a href="tel:+998940158800" class="hover:text-pearl-100">+998 94 015 88 00</a>
            </li>
          </ul>
        </div>

        <div>
          <h4 class="text-sm font-bold text-pearl-100">Biz ijtimoiy tarmoqlarda</h4>
          <div class="mt-4 flex gap-3">
            <a
              v-for="social in [
                { name: 'Instagram', href: 'https://www.instagram.com/sadaf_travel.uz/', path: 'M7 3h10a4 4 0 0 1 4 4v10a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4V7a4 4 0 0 1 4-4Zm5 5.5a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7Zm4.7-1.9a.9.9 0 1 0 0 1.8.9.9 0 0 0 0-1.8Z' },
                { name: 'Telegram', href: 'https://t.me/Sadaf_TravelAgency', path: 'm3 12 17-8-3 17-6-5-3 3-1-6Z' }
              ]"
              :key="social.name"
              :href="social.href"
              target="_blank"
              rel="noopener"
              :aria-label="social.name"
              class="flex h-10 w-10 items-center justify-center rounded-full border border-pearl-100/15 text-pearl-100/70 transition-colors hover:border-nacre-400 hover:text-nacre-400"
            >
              <svg class="h-[18px] w-[18px]" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path :d="social.path" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>