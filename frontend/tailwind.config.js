/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#7C3AED",
        secondary: "#A78BFA",
        cta: "#06B6D4",
        background: "#FAF5FF",
        text: "#1E1B4B",
      },
      fontFamily: {
        heading: ['"Baloo 2"', 'cursive'],
        body: ['"Comic Neue"', 'cursive'],
      },
    },
  },
  plugins: [],
}
