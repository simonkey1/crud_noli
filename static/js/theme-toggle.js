document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.getElementById("theme-toggle");
  const darkIcon = document.getElementById("theme-toggle-dark-icon");
  const lightIcon = document.getElementById("theme-toggle-light-icon");

  // Función auxiliar para mostrar íconos
  function updateIcons(isDark) {
    if (isDark) {
      darkIcon.classList.remove("hidden");
      lightIcon.classList.add("hidden");
    } else {
      lightIcon.classList.remove("hidden");
      darkIcon.classList.add("hidden");
    }
  }

  // 1. Estado inicial: lee localStorage o detecta preferencia del sistema
  const savedTheme = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const isDark = savedTheme === "dark" || (!savedTheme && prefersDark);

  if (isDark) {
    document.documentElement.classList.add("dark");
    updateIcons(true);
  } else {
    document.documentElement.classList.remove("dark");
    updateIcons(false);
  }

  // 2. Cambiar tema al hacer clic
  toggle.addEventListener("click", () => {
    const isDarkNow = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", isDarkNow ? "dark" : "light");
    updateIcons(isDarkNow);
  });
});
