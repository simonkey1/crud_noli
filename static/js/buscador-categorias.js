/**
 * buscador-categorias.js
 * Script para manejar el filtrado y redirección por categorías
 */

document.addEventListener('DOMContentLoaded', function() {
    // Selector para el filtro de categorías
    const categoryFilter = document.getElementById('category-filter');
    
    if (!categoryFilter) {
        console.log('No se encontró el selector de categorías');
        return;
    }
    
    console.log('Inicializando filtro de categorías');
    
    // Verificar si hay categorías en el desplegable
    const options = categoryFilter.querySelectorAll('option');
    console.log(`Categorías encontradas: ${options.length}`);
    
    // Manejar el cambio de categoría
    categoryFilter.addEventListener('change', function() {
        const selectedOption = categoryFilter.options[categoryFilter.selectedIndex];
        const categoryUrl = selectedOption.value;
        
        // Mostrar un indicador de carga
        if (typeof showLoadingOverlay === 'function') {
            showLoadingOverlay('Cargando productos...');
        }
        
        // Si hay una URL válida en la opción seleccionada, redirigir
        if (categoryUrl && categoryUrl.startsWith('/')) {
            console.log('Cambiando a categoría:', categoryUrl);
            
            // Al cambiar de categoría, mantener el tamaño de página pero volver a la página 1
            const limit = new URLSearchParams(window.location.search).get('limit') || 10;
            const q = new URLSearchParams(window.location.search).get('q');
            
            // Construir la URL con parámetros de paginación
            const redirectUrl = `${categoryUrl}?page=1&limit=${limit}${q ? `&q=${encodeURIComponent(q)}` : ''}`;
            window.location.href = redirectUrl;
        }
    });
});
