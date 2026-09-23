<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '90 123 45 67' }
})
const emit = defineEmits(['update:modelValue'])

// "+998 90 123 45 67" -> "901234567" (faqat operator kodi + raqam)
function localDigits(v) {
  let d = String(v || '').replace(/\D/g, '')
  if (d.startsWith('998')) d = d.slice(3)
  return d.slice(0, 9)
}

// "901234567" -> "90 123 45 67"
function pretty(d) {
  const p = [d.slice(0, 2), d.slice(2, 5), d.slice(5, 7), d.slice(7, 9)]
  return p.filter(Boolean).join(' ')
}

const shown = computed(() => pretty(localDigits(props.modelValue)))

function onInput(e) {
  const d = localDigits(e.target.value)
  // Kursor sakramasligi uchun input qiymatini darhol formatlaymiz
  e.target.value = pretty(d)
  emit('update:modelValue', d ? `+998 ${pretty(d)}` : '')
}
</script>

<template>
  <div class="relative">
    <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 select-none text-sm font-medium text-slate-500">
      +998
    </span>
    <input
      :value="shown"
      type="tel"
      inputmode="numeric"
      autocomplete="tel"
      class="field pl-[3.4rem]"
      :placeholder="placeholder"
      @input="onInput"
    />
  </div>
</template>
