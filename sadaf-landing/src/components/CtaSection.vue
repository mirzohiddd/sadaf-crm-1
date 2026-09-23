<script setup>
function scrollToForm() {
  const formSection = document.getElementById('ariza-form')
  formSection?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  formSection?.querySelector('#name')?.focus({ preventScroll: true })
}
</script>

<template>
  <section class="relative overflow-hidden bg-navy-900 py-16 sm:py-20">
    <div class="pointer-events-none absolute inset-x-0 -top-10 h-40 bg-nacre-500/10 blur-3xl"></div>

    <div class="container-page relative flex flex-col items-center gap-6 text-center">
      <h2 class="max-w-xl font-display text-3xl leading-tight text-pearl-100 sm:text-4xl">
        Sayohatingizni bugundan boshlang
      </h2>
      <p class="max-w-md text-sm leading-relaxed text-pearl-100/65 sm:text-base">
        Ariza qoldiring — mutaxassisimiz 24 soat ichida siz bilan bog‘lanib, eng qulay yo‘nalish va narxlarni taklif qiladi.
      </p>
      <button
        type="button"
        class="mt-2 flex items-center gap-2.5 rounded-full bg-coral-500 px-7 py-3.5 text-sm font-bold tracking-wide text-pearl-100 transition-colors hover:bg-coral-600"
        @click="scrollToForm"
      >
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M2.5 12 21 3l-5 18-6-6.5L2.5 12Z" />
        </svg>
        Ariza qoldirish
      </button>
    </div>
  </section>
</template>
