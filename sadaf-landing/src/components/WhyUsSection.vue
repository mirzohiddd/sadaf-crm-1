<script setup>
const features = [
  {
    title: 'Eng yaxshi yo‘nalishlar',
    description: 'Butun dunyo bo‘ylab eng mashhur yo‘nalishlar',
    icon: 'globe'
  },
  {
    title: 'Qulay narxlar',
    description: 'Bizda arzon va shaffof narxlar siyosati',
    icon: 'tag'
  },
  {
    title: 'Ishonch va sifat',
    description: 'Yillar tajribasi va minglab mamnun mijozlar',
    icon: 'badge'
  },
  {
    title: '24/7 qo‘llab-quvvatlash',
    description: 'Har doim siz uchun xizmatdamiz',
    icon: 'support'
  }
]
</script>

<template>
  <section class="bg-pearl-100 py-16 sm:py-20">
    <div class="container-page">
      <div class="text-center">
        <h2 class="font-display text-3xl text-navy-900 sm:text-4xl">Nega aynan biz?</h2>
        <div class="mx-auto mt-3 h-[3px] w-14 rounded-full bg-nacre-500"></div>
      </div>

      <div class="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        <div v-for="feature in features" :key="feature.title" class="text-center">
          <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full border-[1.5px] border-nacre-500/40">
            <svg v-if="feature.icon === 'globe'" class="h-7 w-7 text-nacre-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <circle cx="12" cy="12" r="8.5" />
              <path d="M12 3.5c2.5 2.4 3.8 5.3 3.8 8.5s-1.3 6.1-3.8 8.5c-2.5-2.4-3.8-5.3-3.8-8.5S9.5 5.9 12 3.5Z" />
              <path d="M3.8 9.5h16.4M3.8 14.5h16.4" />
            </svg>
            <svg v-else-if="feature.icon === 'tag'" class="h-7 w-7 text-nacre-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <path d="M12.5 3.5H19a1.5 1.5 0 0 1 1.5 1.5v6.5a1.5 1.5 0 0 1-.44 1.06l-8 8a1.5 1.5 0 0 1-2.12 0l-6.5-6.5a1.5 1.5 0 0 1 0-2.12l8-8c.28-.28.66-.44 1.06-.44Z" />
              <circle cx="16" cy="8" r="1.4" />
            </svg>
            <svg v-else-if="feature.icon === 'badge'" class="h-7 w-7 text-nacre-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <path d="m12 3 2.2 1.7 2.8-.3 1 2.6 2.5 1.3-.6 2.8.6 2.8-2.5 1.3-1 2.6-2.8-.3L12 19l-2.2-1.7-2.8.3-1-2.6-2.5-1.3.6-2.8-.6-2.8 2.5-1.3 1-2.6 2.8.3L12 3Z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            <svg v-else class="h-7 w-7 text-nacre-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">
              <path d="M4 13.5v-2a8 8 0 0 1 16 0v2" />
              <rect x="2.5" y="13" width="4.5" height="6" rx="1.4" />
              <rect x="17" y="13" width="4.5" height="6" rx="1.4" />
              <path d="M19.5 19.5A5.5 5.5 0 0 1 14 24" />
            </svg>
          </div>
          <h3 class="mt-5 text-base font-bold text-navy-900">{{ feature.title }}</h3>
          <p class="mx-auto mt-2 max-w-[220px] text-sm leading-relaxed text-navy-900/60">
            {{ feature.description }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
