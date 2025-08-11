/**
 * refresh-notification.js
 * Script para manejar notificaciones específicas de actualización y botón de refresco
 */

// Función para mostrar notificación con botón de refresco
function showRefreshNotification(message) {
    // Eliminar cualquier notificación de refresco existente
    const existingNotification = document.getElementById('refresh-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // Crear la notificación
    const notification = document.createElement('div');
    notification.id = 'refresh-notification';
    notification.className = 'fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg shadow-lg z-[9999] p-4 flex items-center space-x-4 opacity-0 transition-opacity duration-300';
    
    // Contenido con mensaje y botón
    notification.innerHTML = `
        <div class="flex-shrink-0 text-blue-600 dark:text-blue-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
        </div>
        <div class="flex-1">
            <p class="text-sm font-medium text-blue-700 dark:text-blue-300">${message}</p>
        </div>
        <button id="refresh-button" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-md text-sm font-medium flex items-center space-x-1 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>Actualizar</span>
        </button>
        <button id="close-refresh-notification" class="ml-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-full p-1 hover:bg-gray-200 dark:hover:bg-gray-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;
    
    // Añadir al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.add('opacity-100');
    }, 50);
    
    // Configurar botón de actualizar
    const refreshButton = document.getElementById('refresh-button');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            window.location.reload(true);
        });
    }
    
    // Configurar botón para cerrar
    const closeButton = document.getElementById('close-refresh-notification');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            notification.classList.remove('opacity-100');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
    }
    
    // Auto ocultar después de 10 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('opacity-100');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 10000);
}

// Función para añadir botón flotante de refresco a la interfaz
function addFloatingRefreshButton() {
    // Eliminar botón existente si lo hay
    const existingButton = document.getElementById('floating-refresh-button');
    if (existingButton) {
        existingButton.remove();
    }
    
    // Crear botón flotante
    const refreshButton = document.createElement('button');
    refreshButton.id = 'floating-refresh-button';
    refreshButton.className = 'fixed bottom-6 right-6 bg-amber-600 hover:bg-amber-700 text-white p-3 rounded-full shadow-lg z-[9998] transform transition-transform hover:scale-110';
    refreshButton.title = 'Actualizar página para ver cambios';
    refreshButton.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
    `;
    
    // Añadir al DOM
    document.body.appendChild(refreshButton);
    
    // Configurar clic
    refreshButton.addEventListener('click', () => {
        window.location.reload(true);
    });
}

// Exportar funciones globalmente
window.showRefreshNotification = showRefreshNotification;
window.addFloatingRefreshButton = addFloatingRefreshButton;
