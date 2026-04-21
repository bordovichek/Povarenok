/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        warmbg: '#F7E9D7',
        warm: '#F1C27D',
        warm2: '#E0A96D',
        ink: '#2C2C2C',
        muted: '#6B6B6B',
      },
      boxShadow: {
        card: '0 10px 25px rgba(0,0,0,0.06)',
      },
      borderRadius: {
        card: '16px',
      }
    },
  },
  plugins: [],
}
