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
      },
    },
  },  
  plugins: [
    require('flowbite/plugin')({ datatables: true }),
    // otros...
  ],
};
