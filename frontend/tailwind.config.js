/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#38BDF8', // sky blue
          hover: '#0EA5E9',
          light: '#F0F9FF',
        },
        ink: '#0F172A',
        line: '#E2E8F0',
      },
      fontFamily: {
        sans: ['Pretendard', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
