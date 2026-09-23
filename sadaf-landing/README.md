# SADAF Travel Agency — Landing Page

Vue 3 (Composition API, `<script setup>`) + Vite + Tailwind CSS. Faqat frontend — backend bilan ishlamaydi, faqat mavjud API'ga so'rov yuboradi.

## O'rnatish

```bash
npm install
cp .env.example .env
# .env faylida VITE_API_BASE_URL ni o'z backend manzilingizga o'zgartiring
npm run dev
```

Production build:

```bash
npm run build
npm run preview
```

## Loyiha strukturasi

```
src/
  components/
    SadafLogo.vue      — chig'anoq (shell) logotipi, wordmark bilan
    HeroSection.vue     — hero, headline, form joylashuvi
    LeadForm.vue         — ariza formasi: validatsiya, loading, success/error
    WhyUsSection.vue    — "Nega aynan biz?" 4 ta xususiyat
    CtaSection.vue      — pastki CTA banner
    AppFooter.vue        — footer: aloqa, ijtimoiy tarmoqlar
  services/
    api.js               — POST {VITE_API_BASE_URL}/api/leads
  utils/
    utm.js                — UTM parametrlarni URL'dan o'qib localStorage'ga saqlash
  App.vue
  main.js
  style.css
```

## Backend bilan integratsiya

Frontend hech qanday backend logikasini o'zgartirmaydi yoki yaratmaydi — faqat quyidagi endpoint'ga so'rov yuboradi:

```
POST ${VITE_API_BASE_URL}/api/leads
Content-Type: application/json

{
  "name": "Aziz Karimov",
  "phone": "+998901234567",
  "destination": "Turkiya — Antalya",
  "travelDate": "2026-10-12",
  "utm_source": "instagram",
  "utm_medium": "cpc",
  "utm_campaign": "targetolog_1",
  "utm_content": "",
  "utm_term": ""
}
```

## UTM tracking (3 targetolog uchun)

`src/utils/utm.js` sahifa birinchi marta ochilganda URL'dagi `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` parametrlarini `localStorage`'ga (`sadaf_utm_params` kaliti bilan) saqlaydi. Foydalanuvchi keyinroq formani to'ldirsa ham, saqlangan UTM qiymatlari so'rovga avtomatik qo'shiladi.

Har bir targetolog uchun alohida reklama havolasi:

```
https://sizning-domeningiz.uz/?utm_source=instagram&utm_medium=cpc&utm_campaign=targetolog_1
https://sizning-domeningiz.uz/?utm_source=instagram&utm_medium=cpc&utm_campaign=targetolog_2
https://sizning-domeningiz.uz/?utm_source=instagram&utm_medium=cpc&utm_campaign=targetolog_3
```

Backend tomonda `utm_campaign` bo'yicha filtrlab, qaysi targetologning reklamasi qancha lead keltirganini solishtirish mumkin bo'ladi.

## Dizayn

- Ranglar: to'q ko'k fon (`navy`), inju rangidagi matn (`pearl`), sadaf/mercan aksent (`nacre`, `coral`) — logotipdagi ranglarga mos.
- Shrift: sarlavhalar uchun serif `Cormorant Garamond`, matn uchun `Manrope`.
- Mobile-first, 350px'dan boshlab responsive (`sm`, `lg` breakpoint'lar bilan).
