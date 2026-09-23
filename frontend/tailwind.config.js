/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#0b1b34',
          800: '#0f2440',
          700: '#16304f',
          600: '#1d3c62'
        },
        brand: {
          orange: '#f2812f',
          blue: '#3b82f6'
        },
        canvas: '#f4f7fb'
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'Segoe UI', 'sans-serif']
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,24,40,.04), 0 8px 24px rgba(16,24,40,.05)'
      }
    }
  },
  plugins: []
}
