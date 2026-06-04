/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        agtech: {
          green: '#2d6a4f',
          light: '#52b788',
          yellow: '#d4a017',
          bg: '#f0f4ef',
        },
      },
    },
  },
  plugins: [],
}
