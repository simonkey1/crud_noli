/**
 * loading-overlay.js
 * Script para manejar un overlay de carga global
 */

let loadingOverlay = null;

// Comprobar si ya existe un loading overlay al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const existingOverlay = document.getElementById('loading-overlay');
    if (existingOverlay) {
        loadingOverlay = existingOverlay;
    }
    
    // Añadir botón de actualización
    if (typeof addFloatingRefreshButton === 'function') {
        addFloatingRefreshButton();
    }
});

function showLoadingOverlay() {
    // Eliminar cualquier overlay existente primero para evitar duplicados o bloqueos
    hideLoadingOverlay();

    // Crear el nuevo overlay
    loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loading-overlay';
    loadingOverlay.className = 'fixed inset-0 bg-gray-900/70 dark:bg-gray-900/80 flex items-center justify-center z-[9999]';
    loadingOverlay.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-xl flex items-center">
            <svg class="animate-spin h-6 w-6 text-amber-600 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p class="text-gray-700 dark:text-gray-200 font-medium">Procesando...</p>
        </div>
    `;

    // Agregar al documento
    document.body.appendChild(loadingOverlay);
    
    // Evitar scroll en el body
    document.body.style.overflow = 'hidden';
    
    // Configurar un tiempo máximo para el loading overlay (5 segundos)
    // Esto evita que se quede cargando indefinidamente si hay algún error
    setTimeout(hideLoadingOverlay, 5000);
}

function hideLoadingOverlay() {
    // Buscar el overlay tanto en variable como en DOM
    const overlayInDOM = document.getElementById('loading-overlay');
    
    // Si no hay overlay en ninguna parte, no hacer nada
    if (!loadingOverlay && !overlayInDOM) return;

    // Eliminar el overlay si existe en el DOM
    if (overlayInDOM) {
        document.body.removeChild(overlayInDOM);
    } else if (loadingOverlay && loadingOverlay.parentNode) {
        // O eliminar desde la variable si existe
        document.body.removeChild(loadingOverlay);
    }
    
    // Resetear la variable
    loadingOverlay = null;
    
    // Restaurar scroll
    document.body.style.overflow = '';
}

// Asegurarse de ocultar el loading overlay antes de recargar la página
window.addEventListener('beforeunload', hideLoadingOverlay);

// Establecer un tiempo máximo para el loading overlay (5 segundos)
function setupOverlayTimeout() {
    if (loadingOverlay) {
        setTimeout(() => {
            hideLoadingOverlay();
        }, 3000);
    }
}

// Aplicar listener a todos los botones de tipo "submit" para mejorar la experiencia de usuario
document.addEventListener('DOMContentLoaded', () => {
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Si el botón ya está en estado de carga, no hacer nada
            if (this.disabled) return;
            
            // Almacenar estado original para restaurar si hay error
            const originalText = this.innerHTML;
            
            // Si el botón se presiona nuevamente cuando ya está cargando, forzar recarga
            if (originalText.includes('Actualizando') || originalText.includes('spin')) {
                if (typeof hideLoadingOverlay === 'function') {
                    hideLoadingOverlay();
                }
                window.location.reload(true);
                return;
            }
        });
    });
});
