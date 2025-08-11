/**
 * paginacion.js
 * Script para manejar la paginación de productos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Selector de elementos por página
    const perPageSelect = document.getElementById('per-page-select');
    
    if (!perPageSelect) {
        console.log('No se encontró el selector de elementos por página');
        return;
    }
    
    console.log('Inicializando selector de elementos por página');
    
    // Manejar el cambio de número de elementos por página
    perPageSelect.addEventListener('change', function() {
        const selectedValue = perPageSelect.value;
        console.log(`Cambiando a ${selectedValue} elementos por página`);
        
        // Obtener la URL actual y sus parámetros
        const url = new URL(window.location.href);
        const params = new URLSearchParams(url.search);
        
    // Actualizar o agregar los parámetros de paginación
        params.set('limit', selectedValue);
        params.set('page', '1'); // Volver a la primera página al cambiar el límite
    // Preservar búsqueda si existe
    const q = params.get('q');
        
        // Construir la nueva URL
        url.search = params.toString();
        
        // Mostrar un indicador de carga
        if (typeof showLoadingOverlay === 'function') {
            showLoadingOverlay('Actualizando vista...');
        }
        
        // Redirigir a la nueva URL
        window.location.href = url.toString();
    });
});
