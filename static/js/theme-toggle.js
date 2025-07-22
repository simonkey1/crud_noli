// Esperamos a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {
  // Obtenemos los elementos necesarios
  const toggle = document.getElementById("theme-toggle");
  const darkIcon = document.getElementById("theme-toggle-dark-icon");
  const lightIcon = document.getElementById("theme-toggle-light-icon");

  // Si no existen los elementos necesarios, salir
  if (!toggle) {
    console.log("El elemento theme-toggle no está disponible en esta página");
    return;
  }

  // Función auxiliar para mostrar íconos
  function updateIcons(isDark) {
    if (!darkIcon || !lightIcon) return;
    
    if (isDark) {
      darkIcon.classList.remove("hidden");
      lightIcon.classList.add("hidden");
    } else {
      lightIcon.classList.remove("hidden");
      darkIcon.classList.add("hidden");
    }
  }

  // Obtener el tema actual
  function getCurrentTheme() {
    const savedTheme = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    return savedTheme === "dark" || (!savedTheme && prefersDark);
  }

  // Aplicar el tema actual al cargar la página
  const isDark = getCurrentTheme();
  if (isDark) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
  updateIcons(isDark);

  // Cambiar tema al hacer clic en el botón
  toggle.addEventListener("click", () => {
    const isDarkNow = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", isDarkNow ? "dark" : "light");
    updateIcons(isDarkNow);
  });
});
