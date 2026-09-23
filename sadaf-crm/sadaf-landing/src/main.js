import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { captureUtmParams } from './utils/utm'

// Capture UTM params from the URL (if any) as early as possible so that
// ?utm_source=instagram&utm_campaign=targetolog_1 style links are stored
// before the user interacts with the form.
captureUtmParams()

createApp(App).mount('#app')
