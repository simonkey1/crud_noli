/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "tmeplates/home.html",
    "static/css/input.css"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'FELIXTI'", "system-ui", "sans-serif"],
      },
      colors: {
        primary: "#1d4ed8",
        secondary: "#f59e0b",
        background: "#f3f4f6",
      },
    },
  },
  plugins: [],
};