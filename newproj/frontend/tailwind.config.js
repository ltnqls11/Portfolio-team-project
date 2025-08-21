/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#007AFF',
        'secondary': '#34C759',
        'background': '#F2F2F7',
        'sidebar': 'rgba(255, 255, 255, 0.7)',
        'text-main': '#1C1C1E',
        'text-light': '#8A8A8E',
        'border-color': '#E5E5EA',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.5s ease-out forwards',
      }
    },
  },
  plugins: [
    require('@tailwindcss/aspect-ratio'),
  ],
}