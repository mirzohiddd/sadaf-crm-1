import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import { loadAll } from '@/store'
import { tokenStore } from '@/api'

// Sahifa yangilanganda token bo'lsa ma'lumotlarni oldindan yuklaymiz —
// shunda birinchi ekran bo'sh ko'rinmaydi. Xato bo'lsa router guard hal qiladi.
async function bootstrap() {
  if (tokenStore.get()) {
    try {
      await loadAll()
    } catch {
      // jim o'tamiz — guard login sahifasiga yo'naltiradi
    }
  }
  createApp(App).use(router).mount('#app')
}

bootstrap()
