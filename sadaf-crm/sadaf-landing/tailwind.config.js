/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#0F1128',
          900: '#14162E',
          800: '#1B1E3B',
          700: '#262A52'
        },
        pearl: {
          100: '#FBF3E7',
          200: '#F5E9D8'
        },
        nacre: {
          400: '#E8946B',
          500: '#DD7A4E',
          600: '#C7642F'
        },
        coral: {
          500: '#F0785A',
          600: '#DD5F42'
        }
      },
      fontFamily: {
        display: ['"Cormorant Garamond"', 'serif'],
        body: ['"Manrope"', 'sans-serif']
      },
      boxShadow: {
        card: '0 30px 60px -20px rgba(15, 17, 40, 0.45)'
      },
      backgroundImage: {
        'wave-lines': "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='24' viewBox='0 0 120 24'%3E%3Cpath d='M0 12c10 0 10-8 20-8s10 8 20 8 10-8 20-8 10 8 20 8 10-8 20-8 10 8 20 8' fill='none' stroke='%23DD7A4E' stroke-width='1.5'/%3E%3C/svg%3E\")"
      }
    }
  },
  plugins: []
}
