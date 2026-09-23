# SADAF CRM

Turagentlik uchun to'liq full-stack CRM: Vue 3 frontend + FastAPI backend,
ma'lumotlar JSON fayllarda saqlanadi.

Valyuta: barcha summalar **USD ($)** da.

---

## Tez ishga tushirish

Ikkita terminal kerak.

**Terminal 1 — backend:**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # JWT_SECRET ni o'zgartiring
uvicorn main:app --reload --port 8000
```

**Terminal 2 — frontend:**

```bash
npm install
npm run dev
```

Brauzerda: <http://localhost:5173>

```
login:    admin
password: admin123
```

> Birinchi kirishdan keyin parolni *Sozlamalar → Login va parol* orqali o'zgartiring.

Hodimlar sahifasidan hodim qo'shganingizda unga CRM login, parol va rol beriladi —
shundan keyin ular o'z hisobi bilan kira oladi.

---

## Arxitektura

```
sadaf-crm/
├── backend/                 FastAPI (batafsil: backend/README.md)
│   ├── main.py
│   ├── data/                *.json — barcha CRM ma'lumotlari
│   └── app/
│       ├── storage.py       atomar JSON o'qish/yozish
│       ├── security.py      PBKDF2 + JWT + rol matritsasi
│       ├── deps.py          ruxsat va ko'rish doirasi
│       ├── services/        crm · ai · excel · notify
│       └── routers/         13 ta endpoint guruhi
│
└── src/                     Vue 3
    ├── api/                 ⭐ YANGI — barcha backend so'rovlari
    │   ├── client.js        fetch + JWT + xatoliklar
    │   └── index.js         resurslar bo'yicha modullar
    ├── store/index.js       markaziy holat (backendga ulangan)
    ├── views/               sahifalar
    ├── components/          UI komponentlar
    └── data/mock.js         faqat statik ro'yxatlar (mamlakatlar, bosqichlar)
```

Frontend `/api/...` ga so'rov yuboradi, Vite dev-server uni `localhost:8000` ga
uzatadi (`vite.config.js` → `proxy`). Shu tufayli CORS muammosi yo'q.

JWT token har bir so'rovga `src/api/client.js` ichida **avtomatik** qo'shiladi.
Token eskirsa (401) foydalanuvchi login sahifasiga qaytariladi.

---

## Nima o'zgardi

Mavjud dizayn, komponentlar va UI **saqlab qolindi**. Faqat ma'lumot manbai
almashtirildi:

| Ilgari | Endi |
|---|---|
| `mock.js` dagi statik massivlar | `/api/...` orqali backend |
| `localStorage` da ma'lumot | JSON fayllar serverda |
| `signIn()` — `login === 'admin'` tekshiruvi | JWT + PBKDF2 hash |
| Parol JSON'da ochiq matn | Hash; API'dan hech qachon qaytmaydi |
| Faoliyat jurnali `localStorage` da | `activity.json` |
| `aiAnalyst.js` (brauzerda) | `POST /api/ai/chat` (serverda) |

Ko'p sahifalar — `LeadsView`, `ClientsView`, `ToursView`, `AnalyticsView`,
`BackgroundSettingsView` — **umuman o'zgartirilmadi**, chunki store eski
interfeysni saqladi: `db.leads`, `leadsApi.add()`, `moveLead()`, `saveAppearance()`.

---

## Asosiy imkoniyatlar

**Rollar.** `super_admin` · `admin` · `manager` · `operator`.
Operator faqat o'ziga biriktirilgan leadlar va mijozlarni ko'radi; navbarda
unga yopiq bo'limlar ko'rinmaydi. Backend har bir so'rovni mustaqil tekshiradi —
URL orqali chetlab o'tib bo'lmaydi.

**Dashboard.** Har bir account uchun alohida hisoblanadi: operator — o'z
statistikasi, menejer — jamoasi, admin — hammasi.

**Vazifalar va bildirishnomalar.** Hodimlar bir-biriga topshiriq beradi.
Yangi hodim, lead yoki vazifa yaratilganda bildirishnoma chiqadi; navbarda
o'qilmaganlar soni ko'rinadi (har 60 soniyada yangilanadi).

**Davomat.** Dashboard tepasida Check in / Check out. Ishlangan soat
`attendance.json` da saqlanadi, oylik jami dashboardda ko'rinadi.

**Fon.** Har bir account fonini mustaqil tanlaydi — `settings.json` da `userId`
bo'yicha saqlanadi, boshqa hodimga ta'sir qilmaydi. Mavjud fon dizayni
va 14 ta tayyor rasm o'zgarishsiz qoldi.

**Savdolar.** Lead "To'lov qilindi" yoki "Bron tasdiqlandi" bosqichiga o'tganda
`sales.json` ga avtomatik yozuv tushadi (bosqich orqaga qaytsa — o'chadi).

**Hisobot.** Excel (`openpyxl`) doim ishlaydi.

**AI.** Oddiy suhbatni ("Salom", "Qalaysan?") ham, CRM savollarini ham tushunadi:
"Ali degan mijozni top", "Bugun nechta lead keldi?", "Eng ko'p kim sotdi?".
API kaliti serverda `.env` da; kalit bo'lmasa oflayn rejim ishlaydi.

---

## Production

```bash
npm run build            # dist/ hosil bo'ladi
```

`dist/` ni nginx orqali bering, `/api` ni backendga proxy qiling:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

> `--workers 1` tavsiya etiladi: JSON fayl lock'lari jarayon ichida ishlaydi.
> Yuk oshsa PostgreSQL'ga o'tish vaqti keladi.

Ishga tushirishdan oldin:

- [ ] `JWT_SECRET` o'zgartirildi (`openssl rand -hex 32`)
- [ ] `admin` paroli o'zgartirildi
- [ ] `CORS_ORIGINS` real domenga qo'yildi
- [ ] `backend/data/` uchun zaxira nusxa jadvali sozlandi
