# SADAF CRM — Backend

FastAPI backend. Barcha ma'lumotlar **JSON fayllarda** saqlanadi (`backend/data/`),
hech qanday tashqi baza kerak emas.

---

## 1. O'rnatish

```bash
cd backend

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 2. Sozlash

```bash
cp .env.example .env
```

`.env` faylni oching va kamida `JWT_SECRET` ni o'zgartiring:

```bash
# Xavfsiz kalit yaratish
openssl rand -hex 32
```

| O'zgaruvchi | Nima uchun | Majburiymi |
|---|---|---|
| `JWT_SECRET` | Token imzolash kaliti | **Ha** (productionda) |
| `JWT_EXPIRE_MINUTES` | Token amal muddati (standart 720 = 12 soat) | Yo'q |
| `ADMIN_LOGIN` / `ADMIN_PASSWORD` | Birinchi Super Admin | Yo'q |
| `CORS_ORIGINS` | Frontend manzillari, vergul bilan | Yo'q |
| `ANTHROPIC_API_KEY` | AI yordamchi uchun | Yo'q — bo'sh bo'lsa oflayn rejim |

## 3. Ishga tushirish

```bash
uvicorn main:app --reload --port 8000
```

Birinchi ishga tushishda `data/` papkada JSON fayllar va Super Admin yaratiladi:

```
login:    admin
password: admin123
role:     super_admin
```

> **Muhim:** birinchi kirishdan keyin *Sozlamalar → Login va parol* orqali
> parolni albatta o'zgartiring.

Interaktiv API hujjati: <http://localhost:8000/docs>

---

## Ma'lumot fayllari

```
backend/data/
  users.json          hodimlar + hisob ma'lumotlari (parol PBKDF2 hash)
  leads.json          ledlar
  clients.json        mijozlar
  tours.json          tur paketlari
  sales.json          yopilgan savdolar (leaddan avtomatik)
  tasks.json          vazifalar
  notifications.json  bildirishnomalar
  attendance.json     Check in / Check out
  settings.json       har bir account uchun fon va ko'rinish
  ai_chats.json       AI suhbat tarixi
  activity.json       faoliyat jurnali
```

Yozish **atomar**: avval `.tmp` faylga yoziladi, keyin `os.replace` bilan
almashtiriladi. Har bir fayl uchun alohida lock — parallel so'rovlar
ma'lumotni buzmaydi.

---

## Rollar va huquqlar

| Rol | Ko'radi | Sahifalar |
|---|---|---|
| `super_admin` | Hammasini | Barchasi |
| `admin` | Hammasini | Barchasi (Super Admin hisobiga tegmaydi) |
| `manager` | O'z jamoasini | Barchasi |
| `operator` | Faqat o'ziga biriktirilganni | Dashboard, Ledlar, Mijozlar, Vazifalar, Bildirishnomalar, AI, Sozlamalar |

Menejer jamoasi — `managerId` maydoni orqali biriktiriladi.

Huquqlar **ikki joyda** tekshiriladi: frontend navbarda (qulaylik uchun) va
backend har bir endpointda (xavfsizlik uchun). Frontendni chetlab o'tib
API'ga to'g'ridan-to'g'ri murojaat qilish ish bermaydi.

---

## API

| Prefiks | Vazifasi |
|---|---|
| `/api/auth` | login, me, profil, parol |
| `/api/employees` | hodim hisoblari, `/directory`, `/roles` |
| `/api/leads` | ledlar, `PATCH /{id}/stage` |
| `/api/clients` | mijozlar |
| `/api/tours` | tur paketlari |
| `/api/sales` | savdolar |
| `/api/tasks` | vazifalar, `PATCH /{id}/toggle` |
| `/api/notifications` | bildirishnomalar, `/unread-count` |
| `/api/attendance` | `/check-in`, `/check-out`, `/today`, `/summary` |
| `/api/dashboard` | rolga qarab hisoblangan statistika |
| `/api/analytics` | voronka, menejerlar, yo'nalishlar |
| `/api/reports` | `/excel` |
| `/api/settings` | har bir account uchun fon/ko'rinish |
| `/api/ai` | `/chat`, `/status`, `/history` |
| `/api/integrations/sheets` | `POST /lead` — Google Sheets'dan yangi lead qabul qilish |
| `WS /ws?token=` | real vaqtli sinxronizatsiya (barcha kolleksiyalar) |

Barcha endpointlar (login'dan tashqari) `Authorization: Bearer <token>` talab qiladi.
`/api/integrations/sheets/lead` alohida — u `X-Sheets-Secret` header bilan
himoyalangan (pastga qarang), JWT talab qilmaydi.

---

## Google Sheets integratsiyasi

Google Sheets'ga (masalan Facebook/Instagram Lead Ads formidan) tushadigan
yangi leadlar avtomatik CRM'ga tushishi uchun **Google Apps Script**
ishlatiladi — hech qanday pullik xizmat (Zapier, Make va h.k.) yoki Google
Cloud loyihasi kerak emas.

**Oqim:** Sheet → Apps Script (jadval ichida, bepul) → `POST /api/integrations/sheets/lead` → CRM'da yangi lead.
Yo'nalish bir tomonlama — CRM Sheetsga hech narsa yozmaydi.

### Sozlash

1. `.env` faylda `SHEETS_WEBHOOK_SECRET` ni o'rnating (tasodifiy qatordan
   foydalaning, masalan `openssl rand -hex 24`).
2. Google Sheets'da: **Extensions → Apps Script** → `backend/scripts/google-sheets-webhook.gs`
   faylidagi kodni joylashtiring.
3. Skriptdagi `CRM_URL` (backendingiz manzili) va `SHEETS_SECRET` (1-qadamdagi
   qiymat bilan bir xil) ni to'ldiring.
4. Skript muharriridan `setupTrigger` funksiyasini bir marta ishga tushiring —
   bu `syncNewLeads` uchun har 5 daqiqada ishga tushadigan trigger yaratadi.

### Jadval ustunlari

Skript standart holatda Meta (Facebook/Instagram) Lead Ads eksporti ustun
tartibiga moslangan: `id`, `created_time`, `ad_id`, `ad_name`, `adset_id`,
`adset_name`, `campaign_id`, `campaign_name`, `form_id`, `form_name`,
`is_organic`, `platform`, ism, telefon (xom), `phone_number` (normallashgan),
`lead_status`, `Comment`. Boshqa tartibdagi jadval uchun skriptdagi
`COLUMN_MAP` ni moslang.

CRM'ga quyidagi maydonlar o'tadi: **ism, telefon, sana (created_time'dan),
platforma (Instagram/Facebook — `source` sifatida ham ko'rinadi), campaign,
ad va lead status**. Bular lead yozuvida qo'shimcha maydon sifatida
saqlanadi — mavjud Leads strukturasi (bosqichlar, biriktirish, savdo
sinxronizatsiyasi) o'zgarmaydi.

Dublikat leadlar avval Meta lead ID (`id` ustuni), keyin telefon raqami
bo'yicha aniqlanadi — bir xil lead ikki marta yaratilmaydi.

---

## AI yordamchi

**`ANTHROPIC_API_KEY` berilgan bo'lsa** — model chaqiriladi va unga CRM
qidiruv funksiyalari *tool* sifatida beriladi:

```
search_leads   search_clients   search_sales   search_tasks
get_dashboard_stats             get_employee_stats
```

**Kalit berilmagan bo'lsa** — oflayn (rule-based) rejim ishlaydi. CRM
to'liq ishlayveradi, javoblar soddaroq bo'ladi.

Ikkala rejimda ham funksiyalar **joriy foydalanuvchi doirasida** bajariladi.
Model qanday so'ramasin, operator o'ziga tegishli bo'lmagan ma'lumotni ololmaydi —
filtrlash `services/crm.py` ichida, model qaroridan mustaqil.

API kaliti **faqat backendda** turadi, frontendga hech qachon uzatilmaydi.

---

## Real vaqtli sinxronizatsiya

Backend `/ws` WebSocket endpointini beradi. Har qanday kolleksiya (leadlar,
mijozlar, vazifalar, hodimlar, savdolar va h.k.) JSON faylga yozilganda —
`app/services/realtime.py` barcha ulangan mijozlarga
`{"type": "collection", "collection": "<nom>"}` signalini yuboradi.
Masalan bir hodim ikkinchisiga vazifa bersa, qabul qiluvchi tomonda
vazifa sahifani yangilamasdan darhol paydo bo'ladi. Ulanish `Authorization`
token bilan emas, `?token=` query-parametri bilan autentifikatsiya qilinadi
(brauzer WebSocket'da maxsus header qo'sha olmaydi).

---

## Zaxira nusxa

`data/` papkani nusxalash kifoya:

```bash
tar czf sadaf-backup-$(date +%F).tar.gz data/
```
