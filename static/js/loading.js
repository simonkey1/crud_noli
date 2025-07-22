// static/js/loading.js

// Esperamos a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('loading-overlay');
  
  // Si no existe el overlay, salir
  if (!overlay) {
    console.warn("Elemento loading-overlay no encontrado en el DOM");
    return;
  }
  
  // Asegurar que el overlay esté oculto al inicio
  overlay.classList.add('hidden');
  overlay.classList.remove('flex');
  
  let loadingTimer = null;

  // Definir las funciones de mostrar/ocultar como propiedades de window
  window.showLoading = () => {
    // Limpiar cualquier temporizador existente
    if (loadingTimer) {
      clearTimeout(loadingTimer);
    }
    
    // Solo mostrar después de 150ms para evitar parpadeos en cargas rápidas
    loadingTimer = setTimeout(() => {
      overlay.classList.remove('hidden');
      overlay.classList.add('flex');
    }, 150);
  };

  window.hideLoading = () => {
    // Limpiar el temporizador
    if (loadingTimer) {
      clearTimeout(loadingTimer);
      loadingTimer = null;
    }
    
    // Ocultar el overlay
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
  };

  // Añadir el listener a todos los formularios que no sean el de productos o que no tengan data-no-loading
  document.querySelectorAll('form:not(#product-form):not([data-no-loading])').forEach(form => {
    form.addEventListener('submit', () => window.showLoading());
  });
  
  // Añadir listener para los enlaces que no tienen data-no-loading
  document.querySelectorAll('a:not([data-no-loading])').forEach(link => {
    // Solo activamos en enlaces internos (no externos, no anclas, no javascript:)
    const href = link.getAttribute('href');
    if (href && !href.includes('://') && !href.startsWith('#') && !href.startsWith('javascript:')) {
      link.addEventListener('click', (e) => {
        // No activamos si se presiona Ctrl, Alt, Shift o es botón derecho
        if (e.ctrlKey || e.altKey || e.shiftKey || e.metaKey || e.button !== 0) {
          return;
        }
        
        // Mostrar loading para navegación interna
        window.showLoading();
      });
    }
  });
  
  // Ocultar el overlay inicialmente (por si acaso)
  window.hideLoading();
  
  // Detectar navegación con botones de atrás/adelante del navegador
  window.addEventListener('beforeunload', () => {
    // Solo mostramos el loading si la navegación es a una página interna
    if (document.activeElement.tagName !== 'A' || 
        (document.activeElement.tagName === 'A' && document.activeElement.hasAttribute('data-no-loading'))) {
      window.showLoading();
    }
  });
});
