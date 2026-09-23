<script setup>
defineProps({ name: { type: String, required: true } })
</script>
<template>
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
       stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <template v-if="name === 'home'">
      <path d="M3 10.5 12 3l9 7.5" /><path d="M5 9.5V21h14V9.5" />
    </template>
    <template v-else-if="name === 'user'">
      <circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" />
    </template>
    <template v-else-if="name === 'users'">
      <circle cx="9" cy="8" r="3.5" /><path d="M2 20c0-3.5 3.2-5.5 7-5.5s7 2 7 5.5" /><path d="M17 8.5a3 3 0 1 0 0-1" /><path d="M18 14.5c2.4.5 4 2.2 4 5" />
    </template>
    <template v-else-if="name === 'bag'">
      <rect x="3" y="7" width="18" height="13" rx="2.5" /><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7" />
    </template>
    <template v-else-if="name === 'send'">
      <path d="M21 3 3 10.5l7 2.5 2.5 7L21 3Z" /><path d="m10 13 4.5-4.5" />
    </template>
    <template v-else-if="name === 'pie'">
      <path d="M12 3a9 9 0 1 0 9 9h-9V3Z" /><path d="M15 3.6A9 9 0 0 1 20.4 9H15V3.6Z" />
    </template>
    <template v-else-if="name === 'bars'">
      <path d="M5 20V11" /><path d="M12 20V4" /><path d="M19 20v-6" />
    </template>
    <template v-else-if="name === 'gear'">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 14a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V20a2 2 0 1 1-4 0v-.1A1.6 1.6 0 0 0 7.5 18.4l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 4 12.9H4a2 2 0 1 1 0-4h.1A1.6 1.6 0 0 0 5.6 6.2l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.6 1.6 0 0 0 2.7-1.1V2a2 2 0 1 1 4 0v.1a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7H22a2 2 0 1 1 0 4h-.1a1.6 1.6 0 0 0-1.5 1.3Z" />
    </template>
    <template v-else-if="name === 'dollar'">
      <path d="M12 3v18" /><path d="M16.5 7.5c0-1.7-2-2.5-4.5-2.5s-4.5 1-4.5 3 2 2.6 4.5 3 4.5 1.2 4.5 3-2 3-4.5 3-4.5-.9-4.5-2.6" />
    </template>
    <template v-else-if="name === 'chart'">
      <path d="M4 19h16" /><path d="m5 15 4-5 3.5 3L19 6" />
    </template>
    <template v-else-if="name === 'calendar'">
      <rect x="3" y="5" width="18" height="16" rx="2.5" /><path d="M3 10h18M8 3v4M16 3v4" />
    </template>
    <template v-else-if="name === 'bot'">
      <rect x="4" y="8" width="16" height="12" rx="3" /><path d="M12 4v4" /><circle cx="9" cy="14" r="1" /><circle cx="15" cy="14" r="1" />
    </template>
    <template v-else-if="name === 'bell'">
      <path d="M18 15V10a6 6 0 1 0-12 0v5l-1.5 3h15L18 15Z" /><path d="M10 21h4" />
    </template>
    <template v-else-if="name === 'menu'">
      <path d="M4 7h16M4 12h16M4 17h16" />
    </template>
    <template v-else-if="name === 'close'">
      <path d="M6 6l12 12M18 6 6 18" />
    </template>
    <template v-else-if="name === 'plus'">
      <path d="M12 5v14M5 12h14" />
    </template>
    <template v-else-if="name === 'logout'">
      <path d="M15 17l5-5-5-5" /><path d="M20 12H9" /><path d="M12 20H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h6" />
    </template>
    <template v-else-if="name === 'chevron'">
      <path d="m6 9 6 6 6-6" />
    </template>
    <template v-else-if="name === 'download'">
      <path d="M12 4v11" /><path d="m8 12 4 4 4-4" /><path d="M5 20h14" />
    </template>
    <template v-else-if="name === 'globe'">
      <circle cx="12" cy="12" r="9" /><path d="M3 12h18" /><path d="M12 3c2.5 2.7 3.8 5.7 3.8 9S14.5 18.3 12 21c-2.5-2.7-3.8-5.7-3.8-9S9.5 5.7 12 3Z" />
    </template>
    <template v-else-if="name === 'phone'">
      <path d="M5 4h4l2 5-2.5 1.5a12 12 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1.1 1A16 16 0 0 1 4 5.1 1 1 0 0 1 5 4Z" />
    </template>
    <template v-else-if="name === 'plane'">
      <path d="M10.5 20 12 15l7 3.5V16l-5-4 1-5.5a1.7 1.7 0 1 0-3.4 0L11.5 12l-5 4v2.5L13 15" />
    </template>
    <template v-else-if="name === 'eye'">
      <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z" /><circle cx="12" cy="12" r="2.8" />
    </template>
    <template v-else-if="name === 'pencil'">
      <path d="M4 20h4l10-10a2.5 2.5 0 0 0-3.5-3.5L4.5 16.5 4 20Z" /><path d="m13.5 7 3.5 3.5" />
    </template>
    <template v-else-if="name === 'trash'">
      <path d="M4 7h16" /><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7" />
      <path d="M6.5 7 7.5 20h9L17.5 7" /><path d="M10 11v5M14 11v5" />
    </template>
    <template v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" />
    </template>
    <template v-else-if="name === 'filter'">
      <path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z" />
    </template>
    <template v-else-if="name === 'layers'">
      <path d="m12 3 9 5-9 5-9-5 9-5Z" /><path d="m3 14 9 5 9-5" />
    </template>
    <template v-else-if="name === 'dots'">
      <circle cx="12" cy="5.5" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" />
      <circle cx="12" cy="18.5" r="1.4" fill="currentColor" stroke="none" />
    </template>
    <template v-else-if="name === 'upload'">
      <path d="M12 16V5" /><path d="m8 9 4-4 4 4" /><path d="M5 19h14" />
    </template>
    <template v-else-if="name === 'check-square'">
      <rect x="3.5" y="3.5" width="17" height="17" rx="4" /><path d="m8 12 3 3 5-6" />
    </template>
    <template v-else-if="name === 'x-circle'">
      <circle cx="12" cy="12" r="9" /><path d="m9 9 6 6M15 9l-6 6" />
    </template>
    <template v-else-if="name === 'check-circle'">
      <circle cx="12" cy="12" r="9" /><path d="m8 12 3 3 5-6" />
    </template>
    <template v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" /><path d="M12 7v5.5l3.5 2" />
    </template>
    <template v-else-if="name === 'handshake'">
      <path d="m3 11 3-3 4 3 2-1 2 1 4-3 3 3" /><path d="M6 8v7l4 4 2-2 2 2 4-4V8" />
    </template>
    <template v-else-if="name === 'star'">
      <path d="m12 4 2.4 5 5.6.8-4 3.9 1 5.5-5-2.6-5 2.6 1-5.5-4-3.9 5.6-.8L12 4Z" />
    </template>
    <template v-else-if="name === 'refresh'">
      <path d="M20 12a8 8 0 1 1-2.6-5.9" /><path d="M20 4v4h-4" />
    </template>
    <template v-else-if="name === 'mail'">
      <rect x="3" y="5.5" width="18" height="13" rx="2.5" /><path d="m4 8 8 5 8-5" />
    </template>
    <template v-else-if="name === 'lock'">
      <rect x="4.5" y="10" width="15" height="10" rx="2.5" /><path d="M8 10V7.5a4 4 0 1 1 8 0V10" />
    </template>
    <template v-else-if="name === 'eye-off'">
      <path d="M3 3l18 18" />
      <path d="M10.6 6.3A9.6 9.6 0 0 1 12 6c6.4 0 10 6 10 6a17 17 0 0 1-3.3 3.9" />
      <path d="M6.6 7.9C3.9 9.6 2 12 2 12s3.6 6 10 6a9.9 9.9 0 0 0 4.2-.9" />
      <path d="M9.9 10.1a2.8 2.8 0 0 0 4 3.9" />
    </template>
    <template v-else-if="name === 'copy'">
      <rect x="9" y="9" width="11" height="11" rx="2.5" /><path d="M15 9V6.5A2.5 2.5 0 0 0 12.5 4H6.5A2.5 2.5 0 0 0 4 6.5v6A2.5 2.5 0 0 0 6.5 15H9" />
    </template>
    <template v-else-if="name === 'shield'">
      <path d="M12 3.5 5 6v6c0 4 3 7.2 7 8.5 4-1.3 7-4.5 7-8.5V6l-7-2.5Z" /><path d="m9 12 2 2 4-4" />
    </template>
    <template v-else-if="name === 'message'">
      <path d="M20 15a2 2 0 0 1-2 2H8l-4 3V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v9Z" />
    </template>
    <template v-else-if="name === 'image'">
      <rect x="3" y="4" width="18" height="16" rx="2.5" /><circle cx="8.5" cy="9.5" r="1.5" /><path d="m4 17 5-5 4 4 2.5-2.5L20 17" />
    </template>
    <template v-else-if="name === 'building'">
      <rect x="4" y="3" width="16" height="18" rx="2" /><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2" /><path d="M10 21v-3h4v3" />
    </template>
    <template v-else-if="name === 'camera'">
      <path d="M3 8.5A2 2 0 0 1 5 6.5h2l1.2-2h7.6L17 6.5h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" /><circle cx="12" cy="13" r="3.5" />
    </template>
    <template v-else-if="name === 'arrow-right'">
      <path d="M4 12h15" /><path d="m13 6 6 6-6 6" />
    </template>
    <template v-else-if="name === 'map'">
      <path d="M12 21s7-5.7 7-11a7 7 0 1 0-14 0c0 5.3 7 11 7 11Z" /><circle cx="12" cy="10" r="2.6" />
    </template>
    <template v-else-if="name === 'chat'">
      <path d="M21 12c0 4-4 7-9 7a10.6 10.6 0 0 1-3.2-.5L3 20l1.6-3.5A6.6 6.6 0 0 1 3 12c0-4 4-7 9-7s9 3 9 7Z" />
    </template>
    <template v-else-if="name === 'telegram'">
      <path d="M21.5 4.5 2.8 11.4c-.8.3-.8 1.4.1 1.6l4.8 1.4 1.8 5.3c.2.7 1.1.9 1.6.3l2.5-2.7 4.7 3.5c.6.4 1.4.1 1.6-.6l3-14.5c.2-.8-.6-1.5-1.4-1.2Z" /><path d="m7.7 14.4 10.6-7.6-7.5 8.6" />
    </template>
    <template v-else-if="name === 'chevron-down'">
      <path d="m6 9 6 6 6-6" />
    </template>
  </svg>
</template>
