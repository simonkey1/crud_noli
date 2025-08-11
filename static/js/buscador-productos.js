/**
 * buscador-productos.js
 * Script para manejar la búsqueda y filtrado de productos en la tabla
 */

// Inicialización única y temprana para evitar parpadeos
document.addEventListener('DOMContentLoaded', function() {
    // Si el input viene con valor prellenado (búsqueda en servidor), no aplicar filtro cliente
    const prefilled = (document.getElementById('product-search')?.value || '').trim();
    if (prefilled.length > 0) {
        console.log('Buscador cliente deshabilitado (búsqueda server-side con q)');
        return;
    }
    initBuscador();
});

function initBuscador() {
    console.log('Inicializando buscador de productos v3...');
    
    // Selectores
    const searchInput = document.getElementById('search-input') || document.getElementById('product-search');
    
    // Obtener todas las filas de productos reales (excluyendo posibles filas de mensajes)
    function getProductRows() {
        return document.querySelectorAll('table tbody tr:not(#no-results)');
    }
    
    let tableRows = getProductRows();
    
    // Asegurar que las filas estén visibles pero sin forzar reflujo si ya lo están
    if (tableRows && tableRows.length > 0) {
        tableRows.forEach(row => {
            if (row.style.display === 'none') row.style.display = '';
            row.classList.remove('hidden');
        });
    }
    
    if (!searchInput) {
        console.log('No se encontró el campo de búsqueda');
    } else if (!tableRows.length) {
        console.log('No se encontraron filas de productos en la tabla');
    } else {
        console.log('Inicializando buscador con', tableRows.length, 'productos');
    }
    
    // Función para filtrar productos en tiempo real
    function filterProducts() {
        // Refrescar la lista de filas para asegurarse de que tenemos las actuales
        tableRows = getProductRows();
        
        if (!tableRows || tableRows.length === 0) {
            console.log('No se encontraron filas de productos para filtrar');
            return;
        }
        
        const searchTerm = searchInput ? searchInput.value.toLowerCase().trim() : '';
        
        // Mostrar todos los productos inicialmente
        tableRows.forEach(row => {
            row.style.display = '';
        });
        
        // Si no hay término de búsqueda, asegurarse de mostrar todos los productos
        if (searchTerm === '') {
            // Eliminar mensaje de "no hay resultados" si existe
            const noResultsElement = document.getElementById('no-results');
            if (noResultsElement) {
                noResultsElement.remove();
            }
            return;
        }
        
        let visibleCount = 0;
        
        // Filtrar productos
        tableRows.forEach(row => {
            // Intentar primero con selectores específicos
            try {
                // Intentamos primero con selectores específicos
                const productName = row.querySelector('td:first-child')?.textContent?.toLowerCase() || '';
                const barcode = row.querySelector('td:nth-child(2)')?.textContent?.toLowerCase() || '';
                const category = row.querySelector('td:nth-child(3)')?.textContent?.toLowerCase() || '';
                
                // Verificar si cualquiera de los campos específicos contiene el término de búsqueda
                if (productName.includes(searchTerm) || 
                    barcode.includes(searchTerm) || 
                    category.includes(searchTerm)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    // Si no encuentra en campos específicos, busca en todo el texto
                    const rowText = row.textContent.toLowerCase();
                    if (rowText.includes(searchTerm)) {
                        row.style.display = '';
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                }
            } catch (error) {
                // Si hay un error, simplemente usa el texto completo de la fila
                const rowText = row.textContent.toLowerCase();
                if (rowText.includes(searchTerm)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            }
        });
        
        // Mostrar mensaje si no hay resultados
        const tableBody = document.querySelector('table tbody');
        const noResultsElement = document.getElementById('no-results');
        
        if (visibleCount === 0) {
            if (!noResultsElement) {
                const newRow = document.createElement('tr');
                newRow.id = 'no-results';
                newRow.innerHTML = `
                    <td colspan="8" class="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
                        <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <p class="mt-2 text-lg font-medium">No se encontraron productos</p>
                        <p class="mt-1">Prueba con diferentes criterios de búsqueda</p>
                    </td>
                `;
                tableBody.appendChild(newRow);
            }
        } else if (noResultsElement) {
            noResultsElement.remove();
        }
    }

    // Implementación del filtro de categorías
    function setupCategoryFilter() {
        const categoryFilter = document.getElementById('category-filter');
        if (!categoryFilter) return;
        
        // Verificar si hay categorías en el desplegable
        const options = categoryFilter.querySelectorAll('option');
        console.log(`Categorías encontradas: ${options.length}`);
        
        categoryFilter.addEventListener('change', function() {
            const selectedOption = categoryFilter.options[categoryFilter.selectedIndex];
            const categoryUrl = selectedOption.value;
            
            // Si hay una URL válida en la opción seleccionada, redirigir
            if (categoryUrl && categoryUrl.startsWith('/')) {
                console.log('Cambiando a categoría:', categoryUrl);
                window.location.href = categoryUrl;
            } else {
                // Si es filtro local sin redirección, filtrar en la tabla actual
                filterProducts();
            }
        });
    }
    
    // Agregar evento de entrada al buscador
    if (searchInput) {
        searchInput.addEventListener('input', filterProducts);
        
        // Inicializar el filtro si hay un valor preestablecido
        if (searchInput.value) {
            filterProducts();
        }
    }
    
    // Configurar el filtro de categorías
    setupCategoryFilter();
    
    // Ejecutar un filtro inicial solo si hay valor preestablecido para evitar cambios visuales
    if (searchInput && searchInput.value && searchInput.value.trim() !== '') {
        filterProducts();
    }
};
