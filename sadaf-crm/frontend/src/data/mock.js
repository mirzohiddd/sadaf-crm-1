// Ma'lumotnomalar (select variantlari).
// Bu yerda faqat STATIK ro'yxatlar qoladi — CRM yozuvlari backendda.



export const positions = ['Menejer',]
// Yangi hodim qo'shishda CRM roli faqat "Menejer" bo'ladi
// (backend app/security.py -> /api/employees/roles bilan bir xil; qiymat
// (value) 'admin' bo'lib qoladi — bu backend uchun ID, faqat matn o'zgardi).
export const crmRoles = [
  { value: 'admin', label: 'Menejer' }
]

// Barcha rol nomlari (jadval/eski yozuvlarni ko'rsatish uchun to'liq lug'at)
const ALL_ROLE_LABELS = {
  super_admin: 'Bosh menejer',
  admin: 'Menejer',
  manager: 'Menejer',
  operator: 'Menejer'
}

export const roleLabelOf = (value) => ALL_ROLE_LABELS[value] || value || '—'

export const workShifts = ['To\'liq kun', 'Yarim kun', 'Masofaviy', 'Smenali']
export const countries  = ['Tailand', 'Turkiya', 'BAA', 'Maldivlar', 'Yevropa', 'Misr', 'Gruziya', 'Malayziya']
export const tourStatuses = ['Faol', 'Kam joy', 'Yopiq']
// Kanban bosqichlari — har biriga o'z rangi (ustun sarlavhasi uchun)
export const leadStageList = [
  { name: 'Yangi',                        head: 'bg-sky-600',     edge: 'border-l-sky-600',     icon: 'users' },
  { name: "Mijoz bilan bog'lanilmadi",    head: 'bg-amber-500',   edge: 'border-l-amber-500',   icon: 'clock' },
  { name: "Bog'lanildi",                  head: 'bg-teal-600',    edge: 'border-l-teal-600',    icon: 'phone' },
  { name: 'Taklif yuborildi', head: 'bg-rose-500',    edge: 'border-l-rose-500',    icon: 'message' },
  { name: "To'lov qilindi",   head: 'bg-violet-600',  edge: 'border-l-violet-600',  icon: 'dollar' },
  { name: 'Bron tasdiqlandi', head: 'bg-emerald-600', edge: 'border-l-emerald-600', icon: 'check-circle' },
  { name: 'Bekor qilindi',    head: 'bg-orange-500',  edge: 'border-l-orange-500',  icon: 'x-circle' },
  { name: 'Sifatsiz lead',    head: 'bg-slate-500',   edge: 'border-l-slate-500',   icon: 'filter' }
]

export const leadStages = leadStageList.map((s) => s.name)
export const leadSourceNames = ['Telegram', 'Instagram', 'Sayt', "Qo'ng'iroq"]
export const clientStatuses = ['Faol', 'Yangi', 'Sovuq']

export const countryFlags = {
  Tailand: '🇹🇭', Turkiya: '🇹🇷', BAA: '🇦🇪', Maldivlar: '🇲🇻',
  Yevropa: '🇪🇺', Misr: '🇪🇬', Gruziya: '🇬🇪', Malayziya: '🇲🇾'
}