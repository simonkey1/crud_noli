/**
 * productos-modal.js
 * Script para manejar las funcionalidades de modal para crear y editar productos
 */

document.addEventListener('DOMContentLoaded', function() {
    // Selectores de elementos
    const createModal = document.getElementById('createProductModal');
    const editModal = document.getElementById('editProductModal');
    const deleteModal = document.getElementById('deleteProductModal');
    const openCreateModalBtn = document.getElementById('openCreateModal');
    const closeCreateModalBtn = document.getElementById('closeCreateModal');
    const cancelCreateBtn = document.getElementById('cancelCreate');
    const closeEditModalBtn = document.getElementById('closeEditModal');
    const cancelEditBtn = document.getElementById('cancelEdit');
    const closeDeleteModalBtn = document.getElementById('closeDeleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const editProductForm = document.getElementById('editProductForm');
    const createProductForm = document.getElementById('createProductForm');
    const deleteProductForm = document.getElementById('deleteProductForm');
    const editButtons = document.querySelectorAll('.edit-product-button');
    const deleteButtons = document.querySelectorAll('.delete-product-button');

    // Modal de creación
    if (openCreateModalBtn && createModal) {
        openCreateModalBtn.addEventListener('click', () => {
            createModal.showModal();
        });
    }

    if (closeCreateModalBtn && createModal) {
        closeCreateModalBtn.addEventListener('click', () => {
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = createProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Crear Producto';
                submitBtn.disabled = false;
            }
            createModal.close();
            resetCreateForm();
        });
    }

    if (cancelCreateBtn && createModal) {
        cancelCreateBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = createProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Crear Producto';
                submitBtn.disabled = false;
            }
            createModal.close();
            resetCreateForm();
        });
    }

    // Modal de edición
    if (closeEditModalBtn && editModal) {
        closeEditModalBtn.addEventListener('click', () => {
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = editProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Guardar Cambios';
                submitBtn.disabled = false;
            }
            editModal.close();
        });
    }

    if (cancelEditBtn && editModal) {
        cancelEditBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = editProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Guardar Cambios';
                submitBtn.disabled = false;
            }
            editModal.close();
        });
    }
    
    // Modal de eliminación
    if (closeDeleteModalBtn && deleteModal) {
        closeDeleteModalBtn.addEventListener('click', () => {
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = deleteProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Eliminar';
                submitBtn.disabled = false;
            }
            deleteModal.close();
        });
    }
    
    if (cancelDeleteBtn && deleteModal) {
        cancelDeleteBtn.addEventListener('click', (e) => {
            e.preventDefault();
            // Restaurar botón de envío si hay alguna carga en progreso
            const submitBtn = deleteProductForm.querySelector('button[type="submit"]');
            if (submitBtn && submitBtn.disabled) {
                submitBtn.innerHTML = 'Eliminar';
                submitBtn.disabled = false;
            }
            deleteModal.close();
        });
    }

    // Reinicia el formulario de creación
    function resetCreateForm() {
        if (createProductForm) {
            createProductForm.reset();
        }
    }

    // Manejar envío del formulario de creación con AJAX
    if (createProductForm) {
        createProductForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(createProductForm);
            
            // Cerrar el modal primero para evitar problemas de carga
            if (createModal && typeof createModal.close === 'function') {
                createModal.close();
            }
            
            // Mostrar indicador de carga global
            if (typeof showLoadingOverlay === 'function') {
                showLoadingOverlay();
            }
            
            // Configurar botón
            const submitBtn = createProductForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Guardando...';
            submitBtn.disabled = true;
            
            fetch('/web/productos/crear', {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                // Intentar parsear la respuesta como JSON
                return response.json()
                .then(data => {
                    if (!response.ok) {
                        return Promise.reject(data || { message: 'Error del servidor' });
                    }
                    return data;
                })
                .catch(e => {
                    // Si no se puede parsear como JSON
                    if (!response.ok) {
                        return Promise.reject({ message: 'Error al procesar la respuesta del servidor' });
                    }
                    return { success: response.ok };
                });
            })
            .then(data => {
                if (data.success) {
                    // Ocultar overlay de carga inmediatamente
                    if (typeof hideLoadingOverlay === 'function') {
                        hideLoadingOverlay();
                    }
                    
                    // Mostrar mensaje de éxito
                    showNotification('¡Producto creado con éxito!', 'success');
                    
                    // Mostrar mensaje de actualización y botón flotante
                    if (typeof showRefreshNotification === 'function') {
                        showRefreshNotification('Los cambios se han aplicado. Actualiza para ver los resultados');
                    }
                    
                    if (typeof addFloatingRefreshButton === 'function') {
                        addFloatingRefreshButton();
                    }
                    
                    // Restaurar el botón a su estado original en lugar de recargar automáticamente
                    const submitBtn = document.querySelector('button[type="submit"]');
                    if (submitBtn && submitBtn.disabled) {
                        submitBtn.innerHTML = 'Crear Producto';
                        submitBtn.disabled = false;
                    }
                } else {
                    throw new Error(data.message || 'Error desconocido');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'Error al crear el producto', 'error');
                
                // Ocultar overlay de carga
                if (typeof hideLoadingOverlay === 'function') {
                    hideLoadingOverlay();
                }
                
                // Restaurar botón
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Abrir la modal nuevamente para mostrar el error
                if (createModal) createModal.showModal();
            })
            .finally(() => {
                // Asegurar que el botón se restaure en cualquier caso
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
            });
        });
    }

    // Configurar botones de edición
    if (editButtons) {
        editButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-id');
                
                // Mostrar indicador de carga en el botón
                const originalBtnHTML = this.innerHTML;
                this.innerHTML = '<svg class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
                
                // Cargar datos del producto
                fetch(`/web/productos/${productId}/json`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('No se pudo cargar la información del producto');
                        }
                        return response.json();
                    })
                    .then(producto => {
                        // Restaurar botón
                        this.innerHTML = originalBtnHTML;
                        
                        // Actualizar id oculto para el formulario
                        document.getElementById('edit-id').value = producto.id;
                        
                        // Rellenar el formulario
                        document.getElementById('edit-nombre').value = producto.nombre;
                        document.getElementById('edit-precio').value = producto.precio;
                        document.getElementById('edit-cantidad').value = producto.cantidad;
                        document.getElementById('edit-codigo_barra').value = producto.codigo_barra || '';
                        document.getElementById('edit-umbral_stock').value = producto.umbral_stock || 5;
                        document.getElementById('edit-categoria_id').value = producto.categoria_id || '';
                        
                        // Establecer valores opcionales
                        if (producto.costo !== null && producto.costo !== undefined) {
                            document.getElementById('edit-costo').value = producto.costo;
                        } else {
                            document.getElementById('edit-costo').value = '';
                        }
                        
                        if (producto.margen !== null && producto.margen !== undefined) {
                            document.getElementById('edit-margen').value = producto.margen;
                        } else {
                            document.getElementById('edit-margen').value = '';
                        }
                        
                        // Abrir el modal
                        editModal.showModal();
                    })
                    .catch(error => {
                        // Restaurar botón
                        this.innerHTML = originalBtnHTML;
                        console.error('Error al cargar datos del producto:', error);
                        showNotification('Error al cargar datos del producto', 'error');
                    });
            });
        });
    }
    
    // Configurar botones de eliminación
    if (deleteButtons) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-id');
                const productName = this.getAttribute('data-name');
                
                // Actualizar el formulario de eliminación
                document.getElementById('delete-id').value = productId;
                document.getElementById('delete-product-name').textContent = productName;
                
                // Mostrar modal de confirmación
                deleteModal.showModal();
            });
        });
    }
    
    // Manejar envío del formulario de eliminación con AJAX
    if (deleteProductForm) {
        deleteProductForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const productId = document.getElementById('delete-id').value;
            
            // Cerrar el modal primero para evitar problemas de carga
            if (deleteModal && typeof deleteModal.close === 'function') {
                deleteModal.close();
            }
            
            // Mostrar indicador de carga global
            if (typeof showLoadingOverlay === 'function') {
                showLoadingOverlay();
            }
            
            // Configurar botón
            const submitBtn = deleteProductForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Eliminando...';
            submitBtn.disabled = true;
            
            fetch(`/web/productos/${productId}/eliminar`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                // Intentar parsear la respuesta como JSON
                return response.json()
                .then(data => {
                    if (!response.ok) {
                        return Promise.reject(data || { message: 'Error del servidor' });
                    }
                    return data;
                })
                .catch(e => {
                    // Si no se puede parsear como JSON
                    if (!response.ok) {
                        return Promise.reject({ message: 'Error al procesar la respuesta del servidor' });
                    }
                    return { success: response.ok };
                });
            })
            .then(data => {
                if (data.success) {
                    // Ocultar overlay de carga inmediatamente
                    if (typeof hideLoadingOverlay === 'function') {
                        hideLoadingOverlay();
                    }
                    
                    // Mostrar mensaje de éxito
                    showNotification('¡Producto eliminado con éxito!', 'success');
                    
                    // Mostrar mensaje de actualización y botón flotante
                    if (typeof showRefreshNotification === 'function') {
                        showRefreshNotification('El producto ha sido eliminado. Actualiza para ver los cambios');
                    }
                    
                    if (typeof addFloatingRefreshButton === 'function') {
                        addFloatingRefreshButton();
                    }
                    
                    // Restaurar el botón a su estado original en lugar de recargar automáticamente
                    const submitBtn = document.querySelector('button[type="submit"]');
                    if (submitBtn && submitBtn.disabled) {
                        submitBtn.innerHTML = 'Eliminar';
                        submitBtn.disabled = false;
                    }
                } else {
                    throw new Error(data.message || 'Error desconocido');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'Error al eliminar el producto', 'error');
                
                // Ocultar overlay de carga
                if (typeof hideLoadingOverlay === 'function') {
                    hideLoadingOverlay();
                }
                
                // Restaurar botón
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Abrir la modal nuevamente para mostrar el error
                if (deleteModal) deleteModal.showModal();
            })
            .finally(() => {
                // Asegurar que el botón se restaure en cualquier caso
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
            });
        });
    }

    // Manejar envío del formulario de edición con AJAX
    if (editProductForm) {
        editProductForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            const formData = new FormData(editProductForm);
            const productId = document.getElementById('edit-id').value;
            
            // Cerrar el modal primero para evitar problemas de carga
            if (editModal && typeof editModal.close === 'function') {
                editModal.close();
            }
            
            // Mostrar indicador de carga global
            if (typeof showLoadingOverlay === 'function') {
                showLoadingOverlay();
            }
            
            // Configurar botón
            const submitBtn = editProductForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Actualizando...';
            submitBtn.disabled = true;
            
            fetch(`/web/productos/${productId}/editar`, {
                method: 'POST',
                body: formData,
            })
            .then(response => {
                // Intentar parsear la respuesta como JSON
                return response.json()
                .then(data => {
                    if (!response.ok) {
                        return Promise.reject(data || { message: 'Error del servidor' });
                    }
                    return data;
                })
                .catch(e => {
                    // Si no se puede parsear como JSON
                    if (!response.ok) {
                        return Promise.reject({ message: 'Error al procesar la respuesta del servidor' });
                    }
                    return { success: response.ok };
                });
            })
            .then(data => {
                if (data.success) {
                    // Ocultar overlay de carga inmediatamente
                    if (typeof hideLoadingOverlay === 'function') {
                        hideLoadingOverlay();
                    }
                    
                    // Mostrar mensaje de éxito
                    showNotification('¡Producto actualizado con éxito!', 'success');
                    
                    // Mostrar mensaje de actualización y botón flotante
                    if (typeof showRefreshNotification === 'function') {
                        showRefreshNotification('El producto ha sido actualizado. Actualiza para ver los cambios');
                    }
                    
                    if (typeof addFloatingRefreshButton === 'function') {
                        addFloatingRefreshButton();
                    }
                    
                    // Restaurar el botón a su estado original en lugar de recargar automáticamente
                    const submitBtn = document.querySelector('button[type="submit"]');
                    if (submitBtn && submitBtn.disabled) {
                        submitBtn.innerHTML = 'Guardar Cambios';
                        submitBtn.disabled = false;
                    }
                } else {
                    throw new Error(data.message || 'Error desconocido');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification(error.message || 'Error al actualizar el producto', 'error');
                
                // Ocultar overlay de carga
                if (typeof hideLoadingOverlay === 'function') {
                    hideLoadingOverlay();
                }
                
                // Restaurar botón
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
                
                // Abrir la modal nuevamente para mostrar el error
                if (editModal) editModal.showModal();
            })
            .finally(() => {
                // Asegurar que el botón se restaure en cualquier caso
                if (submitBtn.disabled) {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }
            });
        });
    }

    // Funcionalidad para filtrar productos
    const searchInput = document.getElementById('search-input');
    const categoryFilter = document.getElementById('category-filter');
    const stockFilter = document.getElementById('stock-filter');
    const tableRows = document.querySelectorAll('table tbody tr:not(#no-results)');

    function filterProducts() {
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const categoryTerm = categoryFilter ? categoryFilter.value.toLowerCase() : '';
        const stockTerm = stockFilter ? stockFilter.value.toLowerCase() : '';
        
        let visibleCount = 0;
        
        if (!tableRows || !tableRows.length) return;
        
        tableRows.forEach(row => {
            const productNameElement = row.querySelector('td:first-child .font-medium');
            const barcodeElement = row.querySelector('td:nth-child(2)');
            const categoryElement = row.querySelector('td:nth-child(3)');
            const stockElement = row.querySelector('td:nth-child(7)');
            
            if (!productNameElement || !categoryElement || !stockElement) return;
            
            const productName = productNameElement.textContent.toLowerCase();
            const barcode = barcodeElement ? barcodeElement.textContent.toLowerCase() : '';
            const category = categoryElement.textContent.toLowerCase();
            const stockText = stockElement.textContent.toLowerCase();
            
            let showBySearch = productName.includes(searchTerm) || barcode.includes(searchTerm);
            let showByCategory = !categoryTerm || category.includes(categoryTerm);
            
            let showByStock = true;
            if (stockTerm === 'sin-stock') {
                showByStock = stockText.includes('sin stock');
            } else if (stockTerm === 'bajo-stock') {
                showByStock = stockText.includes('bajo');
            } else if (stockTerm === 'con-stock') {
                showByStock = !stockText.includes('sin stock') && !stockText.includes('bajo');
            }
            
            if (showBySearch && showByCategory && showByStock) {
                row.classList.remove('hidden');
                visibleCount++;
            } else {
                row.classList.add('hidden');
            }
        });
        
        // Si no hay resultados, mostrar mensaje
        const noResultsElement = document.getElementById('no-results');
        if (visibleCount === 0) {
            if (!noResultsElement) {
                const tableBody = document.querySelector('table tbody');
                if (!tableBody) return;
                const newRow = document.createElement('tr');
                newRow.id = 'no-results';
                newRow.innerHTML = `
                    <td colspan="5" class="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
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
    
    // Añadir event listeners si los elementos existen
    if (searchInput) {
        searchInput.addEventListener('input', filterProducts);
        console.log('Buscador activado:', searchInput.id);
    }
    
    // Para el filtro de categorías, necesitamos manejar tanto el cambio de valor como el cambio de URL
    if (categoryFilter) {
        // Para búsqueda local, sin cambio de página
        categoryFilter.addEventListener('input', filterProducts);
        // Para navegación entre categorías
        categoryFilter.addEventListener('change', function() {
            if (this.value) {
                window.location.href = this.value;
            }
        });
        console.log('Filtro de categoría activado:', categoryFilter.id);
    }
    
    if (stockFilter) {
        stockFilter.addEventListener('change', filterProducts);
        console.log('Filtro de stock activado:', stockFilter.id);
    }
    
    // Ejecutar filtro inicial en caso de que haya valores preestablecidos
    if (searchInput || categoryFilter || stockFilter) {
        filterProducts();
    }
    
    // Cálculo automático de precio basado en costo y margen
    function setupPriceCalculation(costoId, margenId, precioId) {
        const costoInput = document.getElementById(costoId);
        const margenInput = document.getElementById(margenId);
        const precioInput = document.getElementById(precioId);
        
        function calculatePrice() {
            const costo = parseFloat(costoInput.value) || 0;
            const margen = parseFloat(margenInput.value) || 0;
            
            if (costo > 0 && margen > 0) {
                const precio = costo / (1 - margen / 100);
                precioInput.value = Math.round(precio);
            }
        }
        
        function calculateMargin() {
            const costo = parseFloat(costoInput.value) || 0;
            const precio = parseFloat(precioInput.value) || 0;
            
            if (costo > 0 && precio > costo) {
                const margen = ((precio - costo) / precio) * 100;
                margenInput.value = margen.toFixed(2);
            }
        }
        
        if (costoInput && margenInput && precioInput) {
            costoInput.addEventListener('input', function() {
                if (margenInput.value) calculatePrice();
                else if (precioInput.value) calculateMargin();
            });
            
            margenInput.addEventListener('input', calculatePrice);
            
            precioInput.addEventListener('input', calculateMargin);
        }
    }
    
    // Configurar cálculo de precios para ambos formularios
    setupPriceCalculation('costo', 'margen', 'precio');
    setupPriceCalculation('edit-costo', 'edit-margen', 'edit-precio');
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        // Eliminar notificaciones anteriores
        const existingNotifications = document.querySelectorAll('.notification-toast');
        existingNotifications.forEach(notification => {
            notification.remove();
        });
        
        // Crear nueva notificación
        const notification = document.createElement('div');
        notification.className = `notification-toast fixed top-6 right-6 z-[9999] p-5 rounded-lg shadow-xl transform transition-all duration-300 ease-in-out opacity-0`;
        
        // Estilos según tipo
        let bgColor, textColor, iconPath;
        switch (type) {
            case 'success':
                bgColor = 'bg-emerald-100 dark:bg-emerald-800';
                textColor = 'text-emerald-800 dark:text-emerald-100';
                iconPath = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>`;
                break;
            case 'error':
                bgColor = 'bg-red-100 dark:bg-red-800';
                textColor = 'text-red-800 dark:text-red-100';
                iconPath = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>`;
                break;
            default:
                bgColor = 'bg-blue-100 dark:bg-blue-800';
                textColor = 'text-blue-800 dark:text-blue-100';
                iconPath = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>`;
        }
        
        notification.classList.add(bgColor, textColor);
        
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        ${iconPath}
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-base font-medium">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button class="notification-close p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.remove('opacity-0');
            notification.classList.add('opacity-100');
        }, 10);
        
        // Configurar botón para cerrar
        const closeBtn = notification.querySelector('.notification-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.classList.add('opacity-0');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            });
        }
        
        // Auto eliminar después de 4 segundos
        setTimeout(() => {
            notification.classList.add('opacity-0', 'translate-x-5');
            setTimeout(() => {
                notification.remove();
            }, 500);
        }, 4000);
    }
});
