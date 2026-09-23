import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { auth, canSee, ui, loadAll } from '@/store'
import { tokenStore } from '@/api'

// `meta.page` — backenddagi ROLE_PAGES bilan bir xil kalitlar.
// Router shu kalit orqali sahifa rolga ochiqligini tekshiradi.

const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard',  name: 'dashboard',  component: () => import('@/views/DashboardView.vue'),  meta: { page: 'dashboard', title: 'Dashboard',  subtitle: "Kunlik statistika va tezkor ko'rsatkichlar" } },
      { path: 'hodimlar',   name: 'hodimlar',   component: () => import('@/views/EmployeesView.vue'),  meta: { page: 'hodimlar',  title: 'Hodimlar',   subtitle: 'Jamoa va ularning natijalari' } },
      { path: 'turlar',     name: 'turlar',     component: () => import('@/views/ToursView.vue'),      meta: { page: 'turlar',    title: 'Turlar',     subtitle: "Tur paketlari va bo'sh joylar" } },
      { path: 'ledlar',     name: 'ledlar',     component: () => import('@/views/LeadsView.vue'),      meta: { page: 'ledlar',    title: 'Ledlar',     subtitle: 'Barcha murojaatlar va ularning bosqichi' } },
      { path: 'mijozlar',   name: 'mijozlar',   component: () => import('@/views/ClientsView.vue'),    meta: { page: 'mijozlar',  title: 'Mijozlar',   subtitle: 'Mijozlar bazasi va sotib olishlar tarixi' } },
      { path: 'savdolar',   name: 'savdolar',   component: () => import('@/views/SalesView.vue'),      meta: { page: 'savdolar',  title: 'Savdolar',   subtitle: 'Yopilgan bitimlar va tushum' } },
      { path: 'analitika',  name: 'analitika',  component: () => import('@/views/AnalyticsView.vue'),  meta: { page: 'analitika', title: 'Analitika',  subtitle: 'Savdo dinamikasi va manbalar taqsimoti' } },
      { path: 'hisobot',    name: 'hisobot',    component: () => import('@/views/ReportsView.vue'),    meta: { page: 'hisobot',   title: 'Hisobot',    subtitle: 'Excel eksport' } },
      {
        path: 'sozlamalar',
        component: () => import('@/views/SettingsView.vue'),
        meta: { page: 'sozlamalar', title: 'Sozlamalar', subtitle: 'Profil va tizim sozlamalari' },
        children: [
          { path: '', redirect: '/sozlamalar/profil' },
          { path: 'profil', name: 'sozlamalar-profil', component: () => import('@/views/settings/ProfileSettingsView.vue'),    meta: { page: 'sozlamalar', title: 'Sozlamalar', subtitle: 'Profil, statistika va faoliyat tarixi' } },
          { path: 'fon',    name: 'sozlamalar-fon',    component: () => import('@/views/settings/BackgroundSettingsView.vue'), meta: { page: 'sozlamalar', title: 'Sozlamalar', subtitle: "Orqa fon va ko'rinish" } },
          { path: 'parol',  name: 'sozlamalar-parol',  component: () => import('@/views/settings/PasswordSettingsView.vue'),   meta: { page: 'sozlamalar', title: 'Sozlamalar', subtitle: 'Login va parolni boshqarish' } }
        ]
      }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

router.beforeEach(async (to) => {
  const authed = !!tokenStore.get() && !!auth.user

  if (!to.meta.public && !authed) return { name: 'login' }
  if (to.meta.public && authed) return { name: 'dashboard' }
  if (!authed) return true

  // Sahifa yangilanganda ma'lumotlar bir marta qayta yuklanadi
  if (!ui.ready && !ui.loading) await loadAll()

  // Rolga yopiq sahifaga to'g'ridan-to'g'ri URL bilan kirishning oldini olamiz
  if (to.meta.page && !canSee(to.meta.page)) return { name: 'dashboard' }

  return true
})

export default router
