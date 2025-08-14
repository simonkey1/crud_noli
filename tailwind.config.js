/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode:'class',  // <<— esto habilita el modo oscuro controlado por clase
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./node_modules/flowbite/**/*.js"
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
        "bg-elegante": '#f1f0ee',
        "bg-beige": '#eaeaea',
        "bg-mint": '#CAE4DB',
        sage: {
          50: '#f6f7f6',
          100: '#e3e8e3',
          200: '#c7d2c7',
          300: '#a3b5a3',
          400: '#7d967d',
          500: '#5f7c5f',
          600: '#4a624a',
          700: '#3c4f3c',
          800: '#323f32',
          900: '#2a352a',
        },
      },
    },
  },  
  plugins: [
    require('flowbite/plugin')({ datatables: true }),
    // otros...
  ],
};
