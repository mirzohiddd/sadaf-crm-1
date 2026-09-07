import { reactive, computed } from 'vue'
import * as api from '@/api'
import { onUnauthorized, tokenStore } from '@/api'
import { connectRealtime, disconnectRealtime } from '@/ws'

// ————————————————————————————————————————————————
//  Markaziy holat
//
//  Ilgari bu yerda mock ma'lumot turardi. Endi hammasi backenddan
//  keladi, lekin komponentlar uchun interfeys o'zgarmagan:
//  db.leads, leadsApi.add(...), moveLead(...) va h.k. avvalgidek ishlaydi.
// ————————————————————————————————————————————————

export const db = reactive({
  employees: [],
  tours: [],
  leads: [],
  clients: [],
  sales: [],
  tasks: [],
  notifications: [],
  activity: [],
  directory: []
})

export const dashboard = reactive({
  stats: [],
  leadSources: [],
  salesSeries: { labels: [], points: [] },
  topDirections: [],
  recentLeads: [],
  bookings: [],
  totals: {},
  scope: 'own'
})

export const analytics = reactive({
  kpi: {},
  salesByDate: { labels: [], points: [] },
  bySource: [],
  funnel: [],
  managers: [],
  byDirection: []
})

export const ui = reactive({
  loading: false,
  error: '',
  ready: false
})

// "Ledlar" menyusi yonidagi belgi — joriy foydalanuvchi hali ko'rmagan
// leadlar soni. Har bir hodim/admin uchun backend alohida hisoblaydi.
export const leadBadge = reactive({ count: 0 })

export async function loadLeadsNewCount() {
  const data = await safe(api.leadsApi.newCount(), null)
  if (data) leadBadge.count = data.count || 0
}

/** Lead ko'rilgach (detal panel/tahrirlash ochilganda) — badge uchun belgilanadi. */
export async function markLeadSeen(id) {
  try {
    await api.leadsApi.markSeen(id)
    loadLeadsNewCount()
  } catch {
    // Jim: badge hisoblagichi keyingi yangilanishda o'zi to'g'irlanadi
  }
}

function fail(err) {
  ui.error = err?.message || "Noma'lum xatolik"
  // Xabar 5 soniyadan keyin o'chadi — foydalanuvchini bezovta qilmaydi
  setTimeout(() => { ui.error = '' }, 5000)
  return null
}

// ————————————————————————————————————————————————
//  Autentifikatsiya
// ————————————————————————————————————————————————

export const auth = reactive({
  user: JSON.parse(localStorage.getItem('sadaf_user') || 'null')
})

export const isAuthed = computed(() => !!auth.user && !!tokenStore.get())

function persistUser(user) {
  auth.user = user
  if (user) localStorage.setItem('sadaf_user', JSON.stringify(user))
  else localStorage.removeItem('sadaf_user')
}

export async function signIn(login, password) {
  try {
    const user = await api.authApi.login(login, password)
    persistUser(user)
    await loadAll()
    connectRealtime(handleRealtimeMessage)
    return true
  } catch (err) {
    ui.error = err?.message || "Login yoki parol noto'g'ri."
    return false
  }
}

export function signOut() {
  api.authApi.logout()
  tokenStore.clear()
  persistUser(null)
  Object.keys(db).forEach((k) => { db[k] = [] })
  leadBadge.count = 0
  ui.ready = false
  disconnectRealtime()
  resetAppearanceLocal()
}

// Token eskirsa — holatni tozalaymiz, router guard login sahifasiga oladi
onUnauthorized(() => {
  persistUser(null)
  ui.ready = false
})

// ——— Rol va ruxsatlar ———

export const role = computed(() => auth.user?.role || 'operator')

export const ROLE_LABELS = {
  super_admin: 'Bosh menejer',
  admin: 'Menejer',
  manager: 'Menejer',
  operator: 'Menejer'
}

export const roleLabel = computed(() => ROLE_LABELS[role.value] || role.value)

/** Sahifa joriy rolga ochiqmi. Navbar shu funksiyaga qaraydi. */
export function canSee(page) {
  const pages = auth.user?.pages
  return Array.isArray(pages) ? pages.includes(page) : true
}

/** Resurs ustida amal bajarish mumkinmi (backend ham alohida tekshiradi). */
export function can(resource, action = 'read') {
  const perms = auth.user?.permissions?.[resource]
  return Array.isArray(perms) ? perms.includes(action) : false
}

export const isAdmin = computed(() => ['super_admin', 'admin'].includes(role.value))

/** Faqat Super Admin — "Mas'ul odam"ni ko'radi/biriktiradi va barcha
 *  adminlarning leadlarini ko'radi. Oddiy Admin faqat o'ziga tegishli
 *  leadlarni ko'radi va mas'ul tanlay olmaydi (backend ham shu tarzda
 *  cheklaydi — bu faqat interfeys uchun). */
export const isSuperAdmin = computed(() => role.value === 'super_admin')

// ————————————————————————————————————————————————
//  Ma'lumotlarni yuklash
// ————————————————————————————————————————————————

async function safe(promise, fallback) {
  try {
    return await promise
  } catch {
    // Ruxsat yo'q bo'lsa (403) — bo'sh ro'yxat, CRM ishlashda davom etadi
    return fallback
  }
}

export async function loadAll() {
  if (!tokenStore.get()) return
  ui.loading = true
  try {
    const [employees, directory, tours, leads, clients, sales, tasks, notifications, activity] =
      await Promise.all([
        safe(api.employeesApi.list(), []),
        safe(api.employeesApi.directory(), []),
        safe(api.toursApi.list(), []),
        safe(api.leadsApi.list(), []),
        safe(api.clientsApi.list(), []),
        safe(api.salesApi.list(), []),
        safe(api.tasksApi.list(), []),
        safe(api.notificationsApi.list(), []),
        safe(api.activityApi.list(), [])
      ])

    Object.assign(db, { employees, directory, tours, leads, clients, sales, tasks, notifications, activity })
    await Promise.all([loadDashboard(), loadAppearance(), loadAttendance(), loadLeadsNewCount()])
    ui.ready = true
    connectRealtime(handleRealtimeMessage) // sahifa yangilansa ham qayta ulanadi
  } finally {
    ui.loading = false
  }
}

export async function loadDashboard() {
  const data = await safe(api.dashboardApi.get(), null)
  if (data) Object.assign(dashboard, data)
}

export async function loadAnalytics() {
  const data = await safe(api.analyticsApi.get(), null)
  if (data) Object.assign(analytics, data)
}

async function refresh(keys = []) {
  const map = {
    employees: () => api.employeesApi.list(),
    directory: () => api.employeesApi.directory(),
    tours: () => api.toursApi.list(),
    leads: () => api.leadsApi.list(),
    clients: () => api.clientsApi.list(),
    sales: () => api.salesApi.list(),
    tasks: () => api.tasksApi.list(),
    notifications: () => api.notificationsApi.list(),
    activity: () => api.activityApi.list()
  }
  await Promise.all(
    keys.filter((k) => map[k]).map(async (key) => {
      const rows = await safe(map[key](), null)
      if (rows) db[key] = rows
    })
  )
}

// ————————————————————————————————————————————————
//  Real vaqtli sinxronizatsiya — WebSocket xabarini qayta ishlash
//
//  Backend qaysi kolleksiya o'zgarganini aytadi ({ collection: 'tasks' }
//  kabi), biz shu bo'limni tinch qayta yuklaymiz. Masalan bir hodim
//  ikkinchisiga vazifa bersa — qabul qiluvchi tomonda ro'yxat va
//  bildirishnoma sahifani yangilamasdan darhol paydo bo'ladi.
// ————————————————————————————————————————————————

const REALTIME_MAP = {
  users: ['employees', 'directory'],
  leads: ['leads'],
  clients: ['clients'],
  sales: ['sales'],
  tasks: ['tasks'],
  tours: ['tours'],
  notifications: ['notifications'],
  activity: ['activity']
}

// Bu bo'limlar o'zgarganda dashboard raqamlari ham eskiradi
const AFFECTS_DASHBOARD = new Set(['leads', 'clients', 'sales', 'tasks', 'tours', 'users'])

function handleRealtimeMessage(data) {
  if (!data || data.type !== 'collection') return
  const collection = data.collection
  const keys = REALTIME_MAP[collection]

  if (keys) refresh(keys)
  if (collection === 'attendance') loadAttendance()
  if (AFFECTS_DASHBOARD.has(collection)) loadDashboard()
  // Yangi lead kelganda yoki biror joyda ko'rilgan deb belgilanganda —
  // "Ledlar" menyusidagi belgi ham darhol yangilanadi.
  if (collection === 'leads') loadLeadsNewCount()
  // 'settings' va 'ai_chats' — shaxsiy ma'lumot, boshqa hodimga signal
  // yuborilmaydi va bu yerda e'tiborsiz qoldiriladi.
}

// Ro'yxatni joyida yangilash (to'liq qayta yuklamasdan)
function upsert(key, row) {
  if (!row) return
  const list = db[key]
  const i = list.findIndex((x) => x.id === row.id)
  if (i === -1) list.unshift(row)
  else list[i] = { ...list[i], ...row }
}

function drop(key, id) {
  const i = db[key].findIndex((x) => x.id === id)
  if (i !== -1) db[key].splice(i, 1)
}

// ————————————————————————————————————————————————
//  CRUD — komponentlar uchun avvalgi shakl (add / update / remove)
// ————————————————————————————————————————————————

function makeCrud(key, client, { after = [] } = {}) {
  return {
    add: async (item) => {
      try {
        const row = await client.create(item)
        upsert(key, row)
        await refresh(['activity', ...after])
        loadDashboard()
        return row
      } catch (err) {
        return fail(err)
      }
    },
    update: async (item) => {
      try {
        const row = await client.update(item.id, item)
        upsert(key, row)
        await refresh(['activity', ...after])
        loadDashboard()
        return row
      } catch (err) {
        return fail(err)
      }
    },
    remove: async (id) => {
      try {
        await client.remove(id)
        drop(key, id)
        await refresh(['activity', ...after])
        loadDashboard()
        return true
      } catch (err) {
        return fail(err)
      }
    }
  }
}

export const employeesApi = makeCrud('employees', api.employeesApi)
export const toursApi = makeCrud('tours', api.toursApi)
export const leadsApi = makeCrud('leads', api.leadsApi, { after: ['sales'] })
export const clientsApi = makeCrud('clients', api.clientsApi)
export const salesApi = makeCrud('sales', api.salesApi)

/** Kanban ustunlari orasida lead ko'chirish. */
export async function moveLead(id, stage) {
  const lead = db.leads.find((l) => l.id === id)
  if (!lead || lead.stage === stage) return
  const previous = lead.stage
  lead.stage = stage // darhol ko'rinsin
  try {
    const row = await api.leadsApi.moveStage(id, stage)
    upsert('leads', row)
    await refresh(['activity', 'sales'])
    loadDashboard()
  } catch (err) {
    lead.stage = previous // xato bo'lsa qaytaramiz
    fail(err)
  }
}

// ——— Vazifalar ———

export const tasksApi = {
  add: async (t) => {
    try {
      const row = await api.tasksApi.create(t)
      upsert('tasks', row)
      refresh(['notifications', 'activity'])
      return row
    } catch (err) {
      return fail(err)
    }
  },
  update: async (t) => {
    try {
      upsert('tasks', await api.tasksApi.update(t.id, t))
    } catch (err) {
      fail(err)
    }
  },
  remove: async (id) => {
    try {
      await api.tasksApi.remove(id)
      drop('tasks', id)
    } catch (err) {
      fail(err)
    }
  },
  toggle: async (id) => {
    const task = db.tasks.find((t) => t.id === id)
    if (task) task.done = !task.done // optimistik
    try {
      upsert('tasks', await api.tasksApi.toggle(id))
      refresh(['notifications', 'activity'])
    } catch (err) {
      if (task) task.done = !task.done
      fail(err)
    }
  }
}

// ——— Bildirishnomalar ———

export const notificationsApi = {
  markRead: async (id) => {
    const n = db.notifications.find((x) => x.id === id)
    if (n?.read) return
    if (n) n.read = true
    try {
      await api.notificationsApi.markRead(id)
    } catch (err) {
      fail(err)
    }
  },
  markAllRead: async () => {
    db.notifications.forEach((n) => { n.read = true })
    try {
      await api.notificationsApi.markAllRead()
    } catch (err) {
      fail(err)
    }
  },
  remove: async (id) => {
    drop('notifications', id)
    try {
      await api.notificationsApi.remove(id)
    } catch (err) {
      fail(err)
    }
  },
  reload: () => refresh(['notifications'])
}

export const unreadCount = computed(() => db.notifications.filter((n) => !n.read).length)

// ——— Davomat ———

export const attendance = reactive({
  checkedIn: false, record: null, days: 0, hours: 0, avgHours: 0
})

export async function loadAttendance() {
  const [today, summary] = await Promise.all([
    safe(api.attendanceApi.today(), null),
    safe(api.attendanceApi.summary(), null)
  ])
  if (today) Object.assign(attendance, { checkedIn: today.checkedIn, record: today.record })
  if (summary) Object.assign(attendance, {
    days: summary.days, hours: summary.hours, avgHours: summary.avgHours
  })
}

export async function checkIn() {
  try {
    attendance.record = await api.attendanceApi.checkIn()
    attendance.checkedIn = true
    await loadAttendance()
  } catch (err) {
    fail(err)
  }
}

export async function checkOut() {
  try {
    attendance.record = await api.attendanceApi.checkOut()
    attendance.checkedIn = false
    await loadAttendance()
  } catch (err) {
    fail(err)
  }
}

// ————————————————————————————————————————————————
//  Faoliyat jurnali (backendda yuritiladi)
// ————————————————————————————————————————————————

const ENTITY_LABEL = {
  lead: 'Lead', client: 'Mijoz', tour: 'Tur',
  employee: 'Hodim', task: 'Vazifa', sale: 'Savdo'
}

export function activityText(a) {
  if (a?.text) return a.text
  const what = ENTITY_LABEL[a?.entity] || a?.entity || ''
  if (a?.action === 'stage') return `${what} bosqichi: ${a.meta?.from} → ${a.meta?.to}`
  if (a?.action === 'create') return `${what} qo'shildi`
  if (a?.action === 'update') return `${what} tahrirlandi`
  if (a?.action === 'delete') return `${what} o'chirildi`
  if (a?.action === 'done') return 'Vazifa bajarildi'
  return what
}

export const loadActivity = () => refresh(['activity'])

// ————————————————————————————————————————————————
//  Ko'rinish sozlamalari (orqa fon)
//
//  Har bir account uchun ALOHIDA: backendda settings.json da
//  userId bo'yicha saqlanadi. Bir hodim fonni o'zgartirsa boshqasiga
//  ta'sir qilmaydi. localStorage faqat tezkor kesh sifatida ishlatiladi
//  va login bo'yicha nomlanadi.
// ————————————————————————————————————————————————

const DEFAULT_ACCENT = '#f08a63'

const DEFAULT_APPEARANCE = {
  mode: 'color',
  color: '#f4f7fb',
  image: '',
  imageSrcset: '',
  dim: 0,
  accent: DEFAULT_ACCENT,
  cardSolidity: 82
}

const cacheKey = () => `sadaf_appearance:${auth.user?.login || 'guest'}`

function readCache() {
  try {
    return JSON.parse(localStorage.getItem(cacheKey()) || 'null')
  } catch {
    return null
  }
}

export const appearance = reactive({ ...DEFAULT_APPEARANCE, ...(readCache() || {}) })

function hexToRgba(hex, a) {
  const n = parseInt(String(hex).slice(1), 16)
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`
}

function shade(hex, amt) {
  const n = parseInt(String(hex).slice(1), 16)
  const f = (v) => Math.max(0, Math.min(255, Math.round(v + v * amt)))
  return '#' + [(n >> 16) & 255, (n >> 8) & 255, n & 255]
    .map((v) => f(v).toString(16).padStart(2, '0')).join('')
}

// Fon rasmi rejimida kartalar biroz shaffof bo'ladi ("shisha" effekti).
function applyCardStyle() {
  const root = document.documentElement
  const onImage = appearance.mode === 'image' && !!appearance.image

  if (!onImage) {
    root.style.setProperty('--card-bg', '#ffffff')
    root.style.setProperty('--card-blur', 'none')
    root.style.setProperty('--card-border', 'rgb(241 245 249)')
    return
  }

  const solidity = Math.max(50, Math.min(100, Number(appearance.cardSolidity ?? 82)))
  root.style.setProperty('--card-bg', `rgba(255, 255, 255, ${solidity / 100})`)
  root.style.setProperty('--card-blur', 'blur(14px) saturate(115%)')
  root.style.setProperty('--card-border', 'rgba(255, 255, 255, .55)')
}

function applyAccent() {
  const c = appearance.accent || DEFAULT_ACCENT
  const root = document.documentElement
  root.style.setProperty('--accent', c)
  root.style.setProperty('--accent-soft', hexToRgba(c, 0.18))
  root.style.setProperty('--accent-ring', hexToRgba(c, 0.35))
  root.style.setProperty('--accent-dark', shade(c, -0.18))
  applyCardStyle()
}

applyAccent()

// Serverga yozishni to'plab yuboramiz — slider surilganda 50 ta so'rov ketmasin
let saveTimer = null
function pushAppearance() {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    api.settingsApi.save({ appearance: { ...appearance } }).catch(() => {})
  }, 400)
}

export function saveAppearance(patch = {}) {
  Object.assign(appearance, patch)
  localStorage.setItem(cacheKey(), JSON.stringify({ ...appearance }))
  applyAccent()
  pushAppearance()
}

export function resetAppearance() {
  saveAppearance({ ...DEFAULT_APPEARANCE })
}

function resetAppearanceLocal() {
  Object.assign(appearance, DEFAULT_APPEARANCE)
  applyAccent()
}

export async function loadAppearance() {
  const row = await safe(api.settingsApi.get(), null)
  if (!row?.appearance) return
  Object.assign(appearance, DEFAULT_APPEARANCE, row.appearance)
  localStorage.setItem(cacheKey(), JSON.stringify({ ...appearance }))
  applyAccent()
}

export function pickWallpaper(w) {
  saveAppearance({ mode: 'image', image: w.url, imageSrcset: w.srcset || '', accent: w.accent })
}

// ——— Tayyor ranglar va fonlar ———

export const presetColors = [
  { name: 'Oq',           value: '#f4f7fb', accent: '#f08a63' },
  { name: 'Navy',         value: '#0f2440', accent: '#f08a63' },
  { name: "Ko'k",         value: '#1d4ed8', accent: '#1d4ed8' },
  { name: 'Yashil',       value: '#047857', accent: '#047857' },
  { name: 'Mayin yashil', value: '#34d399', accent: '#0d9488' },
  { name: 'Kulrang',      value: '#334155', accent: '#475569' },
  { name: "To'q sariq",   value: '#c2410c', accent: '#c2410c' },
  { name: 'Binafsha',     value: '#6d28d9', accent: '#6d28d9' }
]

export const WALLPAPER_WIDTHS = [640, 1280, 1920, 2560]

function wp(id, label, no, accent) {
  const base = `/wallpapers/wp-${String(no).padStart(2, '0')}`
  return {
    id,
    label,
    accent,
    url: `${base}-1920.jpg`,
    thumb: `${base}-640.jpg`,
    srcset: WALLPAPER_WIDTHS.map((w) => `${base}-${w}.jpg ${w}w`).join(', ')
  }
}

export const presetWallpapers = [
  wp('lake',       "Tog' ko'li",       1,  '#165a9d'),
  wp('meadow',     "Yashil o'tloq",    2,  '#1882ad'),
  wp('autumn',     'Kuz xiyoboni',     3,  '#bd411b'),
  wp('cliffs',     'Zakinf qoyalari',  4,  '#1980b0'),
  wp('trail',      "Tumanli so'qmoq",  5,  '#b9651a'),
  wp('galaxy',     "Somon yo'li",      6,  '#4457a8'),
  wp('goldendawn', 'Oltin tong',       7,  '#af4419'),
  wp('mist',       "Tumanli o'rmon",   8,  '#c87c1c'),
  wp('city',       'Nyu-York',         9,  '#b03243'),
  wp('mauritius',  'Mavrikiy',         10, '#1a85bc'),
  wp('tropic',     'Tropik plyaj',     11, '#1a92ba'),
  wp('earth',      'Yer sayyorasi',    12, '#335e8f'),
  wp('forestpath', "Tongdagi so'qmoq", 13, '#5f8a2a'),
  wp('beach',      'Dengiz shomi',     14, '#14878e')
]