// Variables globales
let cart = [];
let discountPercentage = 0;
let discountMode = 'total'; // 'total' o 'item'
let selectedItemForDiscount = null;
let allProducts = [];
let productsByCategory = {};
let stockDisponible = {};

// Verificamos si ya existe un umbral guardado antes de inicializar
let stockUmbral = 5; // Valor por defecto
// Intentamos cargar desde localStorage al principio para evitar problemas de timing
try {
  const umbralGuardadoInicial = localStorage.getItem('stockUmbralPOS');
  if (umbralGuardadoInicial) {
    const umbralNum = parseInt(umbralGuardadoInicial, 10);
    if (!isNaN(umbralNum) && umbralNum >= 1) {
      stockUmbral = umbralNum;
      console.log("Umbral inicial cargado:", stockUmbral);
    }
  } else {
    console.log("No hay umbral guardado inicialmente, usando valor predeterminado:", stockUmbral);
  }
} catch (e) {
  console.error("Error al cargar el umbral inicial:", e);
}

// Referencias a elementos DOM
const productsSection = document.getElementById('products-section');
const cartItemsEl = document.getElementById('cart-items');
const emptyCartEl = document.getElementById('empty-cart');
const cartTotalEl = document.getElementById('cart-total');
const cartDiscountEl = document.getElementById('cart-discount');
const readyBtn = document.getElementById('ready-btn');
const checkoutBtn = document.getElementById('checkout-btn');
const discountBtns = document.querySelectorAll('.discount-btn');
const customDiscountBtn = document.getElementById('custom-discount-btn');
const resetDiscountBtn = document.getElementById('reset-discount-btn');
const discountTotalBtn = document.getElementById('discount-total-btn');
const discountItemBtn = document.getElementById('discount-item-btn');
const clearBtn = document.getElementById('clear-btn');
const paymentSelect = document.getElementById('payment-method');

// Formateo de moneda
function formatCurrency(amount) {
  return new Intl.NumberFormat('es-CL',
    { style: 'currency', currency: 'CLP', minimumFractionDigits: 0 }
  ).format(amount);
}

// Cargar umbral de stock desde localStorage - esta función se ejecuta UNA SOLA VEZ al inicio
function cargarUmbral() {
  try {
    console.log("==== INICIO cargarUmbral ====");
    console.log("1. Valor actual del umbral en memoria:", stockUmbral);
    
    // Verificar si existe la clave antigua y migrarla
    if (localStorage.getItem('stockUmbral')) {
      const valorAntiguo = localStorage.getItem('stockUmbral');
      console.log("2. Encontrada clave antigua 'stockUmbral' con valor:", valorAntiguo);
      localStorage.removeItem('stockUmbral');
      
      // Si no existe la nueva clave pero sí la antigua, migramos el valor
      if (!localStorage.getItem('stockUmbralPOS') && valorAntiguo) {
        localStorage.setItem('stockUmbralPOS', valorAntiguo);
        console.log("3. Migrado valor antiguo a nueva clave:", valorAntiguo);
      }
    }
    
    // Cargar umbral desde localStorage si existe
    const umbralGuardado = localStorage.getItem('stockUmbralPOS');
    console.log("4. Valor actual en localStorage 'stockUmbralPOS':", umbralGuardado);
    
    if (umbralGuardado) {
      const umbralNum = parseInt(umbralGuardado, 10);
      // Verificar que es un número válido
      if (!isNaN(umbralNum) && umbralNum >= 1) {
        stockUmbral = umbralNum;
        console.log("5. Umbral válido cargado:", stockUmbral);
      } else {
        console.log("5. Valor guardado NO válido:", umbralGuardado);
        // Si el valor guardado no es válido, eliminarlo
        localStorage.removeItem('stockUmbralPOS');
        // Establecer un valor por defecto
        stockUmbral = 5;
        console.log("6. Establecido umbral por defecto:", stockUmbral);
      }
    } else {
      console.log("5. No hay umbral guardado en localStorage");
      // Si no hay nada guardado, establecer un valor por defecto
      stockUmbral = 5;
      console.log("6. Establecido umbral por defecto:", stockUmbral);
    }
    
    // SIEMPRE guardar el valor final en localStorage para asegurar consistencia
    localStorage.setItem('stockUmbralPOS', stockUmbral.toString());
    
    // VERIFICAR que realmente se guardó
    const umbralVerificado = localStorage.getItem('stockUmbralPOS');
    console.log("7. Verificación del valor guardado:", umbralVerificado);
    
    if (umbralVerificado !== stockUmbral.toString()) {
      console.error("8. ERROR: El valor guardado no coincide con el esperado");
    } else {
      console.log("8. Verificación correcta: valor guardado coincide");
    }
    
    console.log("==== FIN cargarUmbral ====");
  } catch (error) {
    console.error("Error al cargar el umbral de stock:", error);
    stockUmbral = 5; // En caso de error, aseguramos un valor por defecto
  }
  
  // Actualizar el elemento en el DOM cuando esté listo
  const umbralActualEl = document.getElementById('umbral-actual');
  if (umbralActualEl) {
    umbralActualEl.textContent = stockUmbral;
  } else {
    console.warn("No se encontró el elemento 'umbral-actual' en el DOM");
  }
  
  return stockUmbral; // Devolvemos el valor para poder usarlo donde se llame a esta función
}

// Cargar productos desde el servidor
async function loadProducts() {
  const res = await fetch('/pos/products');
  const prods = await res.json();
  allProducts = prods; // Guardar todos los productos
  
  // Organizar por categoría
  productsByCategory = prods.reduce((acc, p) => {
    const cat = p.categoria?.nombre || 'Otros';
    (acc[cat] = acc[cat] || []).push(p);
    
    // Inicializar el stock disponible para cada producto
    stockDisponible[p.id] = p.cantidad;
    
    return acc;
  }, {});
  
  // Ya no necesitamos verificar el umbral aquí, lo hemos centralizado en cargarUmbral()
  console.log("loadProducts: usando umbral:", stockUmbral);
  
  console.log("Cargando productos con umbral:", stockUmbral);
  
  // Llenar el selector de categorías
  const categoryFilter = document.getElementById('category-filter');
  categoryFilter.innerHTML = '<option value="">Todas las categorías</option>';
  
  // Ordenar categorías alfabéticamente
  const sortedCategories = Object.keys(productsByCategory).sort();
  
  sortedCategories.forEach(cat => {
    const option = document.createElement('option');
    option.value = cat;
    option.textContent = `${cat} (${productsByCategory[cat].length})`;
    categoryFilter.appendChild(option);
  });
  
  renderProducts(productsByCategory);
  
  // Evento para filtrar por categoría
  categoryFilter.addEventListener('change', filterByCategory);
}

// Función para filtrar por categoría
function filterByCategory() {
  const categoryFilter = document.getElementById('category-filter');
  const selectedCategory = categoryFilter.value;
  
  if (!selectedCategory) {
    // Si no hay categoría seleccionada, mostrar todas
    renderProducts(productsByCategory);
  } else {
    // Filtrar solo por la categoría seleccionada
    const filteredProducts = {};
    filteredProducts[selectedCategory] = productsByCategory[selectedCategory];
    renderProducts(filteredProducts);
  }
}

// Función auxiliar para actualizar la visualización de un producto según el umbral
function actualizarVisualizacionStock(stockDisplay, stockActual) {
  if (!stockDisplay) return;
  
  console.log(`Actualizando visualización stock: ${stockActual} con umbral: ${stockUmbral}`);
  
  if (stockActual <= 0) {
    stockDisplay.innerHTML = '<span class="text-red-500">Sin stock</span>';
  } else if (stockActual <= stockUmbral) {
    stockDisplay.innerHTML = `<span class="text-amber-500">Stock bajo: ${stockActual}</span>`;
    console.log(`Producto marcado como stock bajo porque ${stockActual} <= ${stockUmbral}`);
  } else {
    stockDisplay.textContent = `Stock: ${stockActual}`;
    console.log(`Producto con stock normal porque ${stockActual} > ${stockUmbral}`);
  }
}

// Renderizar productos en la interfaz
function renderProducts(byCat) {
  productsSection.innerHTML = '';
  for (const [cat, items] of Object.entries(byCat)) {
    const section = document.createElement('section');
    section.className = 'space-y-4';
    section.innerHTML = `
      <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">${cat}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3"></div>
    `;
    const grid = section.querySelector('div');
    items.forEach(p => {
      // Ya no necesitamos verificar el umbral aquí, usamos el valor global que ya se inicializó
      // en cargarUmbral() al inicio de la aplicación
      
      // Obtener el stock actual (restando lo que ya está en el carrito)
      const stockActual = stockDisponible[p.id];
      
      const btn = document.createElement('button');
      btn.className = 'product-btn group text-left';
      btn.dataset.id = p.id;
      btn.dataset.price = p.precio;
      btn.dataset.name = p.nombre;
      btn.dataset.stock = stockActual; // Añadir el stock como atributo
      btn.disabled = stockActual <= 0;
      
      // Preparar el HTML para mostrar el stock según el umbral actual
      let stockHtml = '';
      console.log(`Renderizando producto con stock ${stockActual}, umbral actual: ${stockUmbral}`);
      if (stockActual <= 0) {
        stockHtml = '<span class="text-red-500">Sin stock</span>';
      } else if (stockActual <= stockUmbral) {
        stockHtml = `<span class="text-amber-500">Stock bajo: ${stockActual}</span>`;
        console.log(`Marcado como stock bajo: ${stockActual} <= ${stockUmbral}`);
      } else {
        stockHtml = `Stock: ${stockActual}`;
        console.log(`Stock normal: ${stockActual} > ${stockUmbral}`);
      }
      
      btn.innerHTML = `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 transition-all duration-200 
                  ${stockActual<=0?'opacity-50 cursor-not-allowed':'hover:shadow-md hover:border-sage-300 dark:hover:border-sage-600'}">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-medium text-gray-900 dark:text-gray-100">${p.nombre}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">${formatCurrency(p.precio)}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 stock-display" data-id="${p.id}">
                ${stockHtml}
              </p>
            </div>
            <div class="w-8 h-8 bg-sage-100 dark:bg-sage-800 rounded-full flex items-center justify-center
                        ${stockActual>0?'group-hover:bg-sage-200 dark:group-hover:bg-sage-700':''} transition-colors duration-200">
              <svg class="w-4 h-4 text-sage-600 dark:text-sage-300" fill="none" stroke="currentColor"
                   viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
              </svg>
            </div>
          </div>
        </div>
      `;
      btn.addEventListener('click', () => addToCart(p.id, p.nombre, p.precio));
      grid.appendChild(btn);
    });
    productsSection.appendChild(section);
  }
}

// Agregar producto al carrito
function addToCart(id, name, price) {
  // Verificar si hay stock disponible
  if (stockDisponible[id] <= 0) {
    // Mostrar mensaje de error
    alert('No hay suficiente stock disponible');
    return;
  }
  
  // Actualizar stock disponible
  stockDisponible[id]--;
  
  // Actualizar botón si corresponde
  const botonProducto = document.querySelector(`.product-btn[data-id="${id}"]`);
  if (botonProducto) {
    botonProducto.dataset.stock = stockDisponible[id];
    if (stockDisponible[id] <= 0) {
      botonProducto.disabled = true;
    }
    
    // Actualizar texto de stock usando la función auxiliar
    const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
    actualizarVisualizacionStock(stockDisplay, stockDisponible[id]);
  }
  
  // Agregar al carrito
  const it = cart.find(x => x.producto_id === id);
  if (it) it.cantidad++;
  else cart.push({ producto_id: id, nombre: name, precio_unitario: price, cantidad: 1 });
  renderCart(); updateCartState();
}

// Quitar producto del carrito
function removeFromCart(id) {
  const idx = cart.findIndex(x => x.producto_id === id);
  if (idx < 0) return;
  
  // Restaurar stock disponible
  stockDisponible[id]++;
  
  // Actualizar botón si corresponde
  const botonProducto = document.querySelector(`.product-btn[data-id="${id}"]`);
  if (botonProducto) {
    botonProducto.disabled = false;
    botonProducto.dataset.stock = stockDisponible[id];
    
    // Actualizar texto de stock usando la función auxiliar
    const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
    actualizarVisualizacionStock(stockDisplay, stockDisponible[id]);
  }
  
  // Quitar del carrito
  cart[idx].cantidad--;
  if (cart[idx].cantidad <= 0) cart.splice(idx, 1);
  renderCart(); updateCartState();
}

// Calcular descuento
function calculateDiscount(amount, percentage) {
  return Math.round(amount * (percentage / 100));
}

// Aplicar descuento
function applyDiscount() {
  // Reset item-specific discount class if we're in total mode
  if (discountMode === 'total') {
    document.querySelectorAll('.cart-item').forEach(el => {
      el.classList.remove('discount-selected');
    });
    selectedItemForDiscount = null;
  }
  
  renderCart();
}

// Renderizar carrito
function renderCart() {
  cartItemsEl.innerHTML = '';
  if (!cart.length) {
    cartItemsEl.appendChild(emptyCartEl);
    cartTotalEl.textContent = formatCurrency(0);
    cartDiscountEl.textContent = formatCurrency(0);
    return;
  }
  if (emptyCartEl.parentNode) emptyCartEl.remove();
  
  let subtotal = 0;
  let discountAmount = 0;
  
  cart.forEach(item => {
    const itemTotal = item.precio_unitario * item.cantidad;
    subtotal += itemTotal;
    
    // Aplicar descuento por producto si corresponde
    let itemDiscount = 0;
    if (discountMode === 'item' && selectedItemForDiscount === item.producto_id) {
      itemDiscount = calculateDiscount(itemTotal, discountPercentage);
      item.descuento = itemDiscount;
    } else if (discountMode === 'item') {
      item.descuento = 0;
    }
    
    const el = document.createElement('div');
    el.className = `flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cart-item ${
      discountMode === 'item' && selectedItemForDiscount === item.producto_id ? 'discount-selected border border-blue-400 dark:border-blue-500' : ''
    }`;
    el.dataset.id = item.producto_id;
    
    el.innerHTML = `
      <div class="flex items-center space-x-3">
        <button class="w-6 h-6 bg-red-100 dark:bg-red-800 hover:bg-red-200 dark:hover:bg-red-700 text-red-600 dark:text-red-200 rounded-full
                       flex items-center justify-center text-sm font-medium"
                onclick="removeFromCart(${item.producto_id})">−</button>
        <div>
          <p class="font-medium text-gray-900 dark:text-gray-100 text-sm">${item.nombre}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">x${item.cantidad} @ ${formatCurrency(item.precio_unitario)}</p>
          ${itemDiscount > 0 ? `<p class="text-xs text-red-500 dark:text-red-400">-${formatCurrency(itemDiscount)}</p>` : ''}
        </div>
      </div>
      <div class="text-right">
        <span class="font-medium text-gray-900 dark:text-gray-100">${formatCurrency(itemTotal - itemDiscount)}</span>
        ${discountMode === 'item' ? `<button onclick="selectItemForDiscount(${item.producto_id})" class="ml-2 px-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-800 dark:bg-blue-900/50 dark:hover:bg-blue-800 dark:text-blue-300 rounded">Desc</button>` : ''}
      </div>
    `;
    cartItemsEl.appendChild(el);
    
    // Sumar descuentos por producto
    if (item.descuento) {
      discountAmount += item.descuento;
    }
  });
  
  // Calcular descuento al total si aplica
  if (discountMode === 'total' && discountPercentage > 0) {
    discountAmount = calculateDiscount(subtotal, discountPercentage);
  }
  
  // Mostrar descuento
  cartDiscountEl.textContent = formatCurrency(discountAmount);
  
  // Calcular total final
  const finalTotal = subtotal - discountAmount;
  cartTotalEl.textContent = formatCurrency(finalTotal);
}

// Seleccionar ítem para descuento
function selectItemForDiscount(productId) {
  if (discountMode !== 'item') return;
  
  if (selectedItemForDiscount === productId) {
    selectedItemForDiscount = null;
  } else {
    selectedItemForDiscount = productId;
  }
  
  applyDiscount();
}

// Actualizar estado del carrito
function updateCartState() {
  const has = cart.length > 0;
  readyBtn.disabled = !has;
  checkoutBtn.disabled = paymentSelect.disabled; // Solo habilitamos el botón de cobrar si el método de pago está habilitado
}

// Función para recargar stock en tiempo real (útil para múltiples clientes)
async function actualizarStockEnTiempoReal() {
  try {
    // Verificamos que estemos usando el umbral correcto guardado en localStorage
    const umbralGuardado = localStorage.getItem('stockUmbralPOS');
    console.log("actualizarStockEnTiempoReal: umbral en localStorage:", umbralGuardado, "umbral actual:", stockUmbral);
    
    if (umbralGuardado) {
      const umbralNum = parseInt(umbralGuardado, 10);
      if (!isNaN(umbralNum) && umbralNum >= 1) {
        if (stockUmbral !== umbralNum) {
          console.log(`Actualizando umbral de ${stockUmbral} a ${umbralNum} desde localStorage`);
          stockUmbral = umbralNum;
          
          // Actualizar también el elemento en el DOM
          const umbralActualEl = document.getElementById('umbral-actual');
          if (umbralActualEl) {
            umbralActualEl.textContent = stockUmbral;
          }
        }
      }
    }
    
    const res = await fetch('/pos/products');
    const prods = await res.json();
    
    // Para cada producto, actualizar el stock teniendo en cuenta lo que hay en el carrito
    prods.forEach(p => {
      // Calcular cuántos están en el carrito actualmente
      const itemEnCarrito = cart.find(item => item.producto_id === p.id);
      const cantidadEnCarrito = itemEnCarrito ? itemEnCarrito.cantidad : 0;
      
      // Actualizar stock disponible
      stockDisponible[p.id] = p.cantidad - cantidadEnCarrito;
    });
    
    // Actualizar visualización de productos sin volver a renderizar toda la página
    document.querySelectorAll('.product-btn').forEach(btn => {
      const id = parseInt(btn.dataset.id);
      const stockActual = stockDisponible[id];
      
      // Actualizar estado del botón
      btn.disabled = stockActual <= 0;
      btn.dataset.stock = stockActual;
      
      // Actualizar texto de stock usando la función auxiliar
      const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
      actualizarVisualizacionStock(stockDisplay, stockActual);
    });
    
    console.log("Stock actualizado en tiempo real. Umbral actual:", stockUmbral);
  } catch (error) {
    console.error("Error al actualizar stock:", error);
  }
}

// Función para filtrar productos
function filterProducts(searchTerm) {
  // Obtener la categoría seleccionada actual
  const categoryFilter = document.getElementById('category-filter');
  const selectedCategory = categoryFilter.value;
  
  if (!searchTerm && !selectedCategory) {
    // Si no hay término de búsqueda ni categoría, mostrar todo organizado por categoría
    renderProducts(productsByCategory);
    return;
  }
  
  // Preparar para filtrado
  let filteredProducts = [...allProducts];
  
  if (searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    
    // Filtrar productos que coinciden con el término de búsqueda
    filteredProducts = filteredProducts.filter(p => 
      p.nombre.toLowerCase().includes(searchTerm) || 
      (p.codigo_barra && p.codigo_barra.toLowerCase().includes(searchTerm)) ||
      (p.categoria && p.categoria.nombre.toLowerCase().includes(searchTerm))
    );
  }
  
  // Aplicar filtro adicional por categoría si está seleccionada
  if (selectedCategory) {
    filteredProducts = filteredProducts.filter(p => 
      (p.categoria?.nombre || 'Otros') === selectedCategory
    );
  }
  
  // Organizar los productos filtrados por categoría
  const filteredByCategory = filteredProducts.reduce((acc, p) => {
    const cat = p.categoria?.nombre || 'Otros';
    (acc[cat] = acc[cat] || []).push(p);
    return acc;
  }, {});
  
  renderProducts(filteredByCategory);
}

// Configuración de eventos al cargar el DOM
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM cargado - Valor de stockUmbral antes de cargar:", stockUmbral);
  
  // Cargar el umbral de localStorage al inicio - SOLO UNA VEZ
  cargarUmbral();
  console.log("Después de cargarUmbral:", stockUmbral);
  
  // Configuración del umbral de stock
  const umbralActualEl = document.getElementById('umbral-actual');
  const configStockBtn = document.getElementById('config-stock-btn');
  
  // Ya no necesitamos actualizar el elemento aquí, lo hace cargarUmbral()
  console.log("Elemento umbral actual:", umbralActualEl?.textContent || "no encontrado");
  
  // Botón para configurar umbral de stock
  if (configStockBtn) {
    configStockBtn.addEventListener('click', () => {
      const nuevoUmbral = prompt("Ingrese el umbral para considerar stock bajo (1-100):", stockUmbral);
      if (nuevoUmbral === null) return; // Cancelado
      
      const umbralNum = parseInt(nuevoUmbral, 10);
      if (isNaN(umbralNum) || umbralNum < 1 || umbralNum > 100) {
        alert("Por favor ingrese un valor válido entre 1 y 100");
        return;
      }
      
      console.log("==== CONFIGURANDO NUEVO UMBRAL ====");
      console.log(`1. Cambiando umbral de ${stockUmbral} a ${umbralNum}`);
      stockUmbral = umbralNum;
      
      // Guardar en localStorage para persistencia entre sesiones con una clave específica para POS
      try {
        // Limpiamos cualquier valor antiguo para evitar conflictos
        localStorage.removeItem('stockUmbral');
        
        // Verificamos primero si hay algo guardado
        const valorAnterior = localStorage.getItem('stockUmbralPOS');
        console.log(`2. Valor anterior en localStorage: ${valorAnterior}`);
        
        // Guardar nuevo valor - usar setItem directamente
        localStorage.setItem('stockUmbralPOS', umbralNum.toString());
        
        // Verificar que se guardó correctamente - leer inmediatamente después
        const valorGuardado = localStorage.getItem('stockUmbralPOS');
        console.log(`3. Umbral guardado en localStorage: ${valorGuardado}`);
        
        if (valorGuardado !== umbralNum.toString()) {
          console.error("4. ¡ERROR! El valor guardado no coincide con el esperado");
          alert("Ocurrió un error al guardar la configuración. Inténtelo de nuevo.");
        } else {
          console.log(`4. Verificación correcta: umbral guardado = ${valorGuardado}`);
        }
        
        // Forzar que otras partes del código lean el nuevo valor
        window.dispatchEvent(new Event('storage'));
      } catch (error) {
        console.error("Error al guardar el umbral en localStorage:", error);
        alert("No se pudo guardar la configuración debido a un error. Inténtelo de nuevo.");
      }
      
      // Actualizar el UI
      if (umbralActualEl) {
        umbralActualEl.textContent = umbralNum;
      }
      
      // Utilizar la función centralizada para actualizar todos los productos
      actualizarVisualizacionTodosProductos();
      
      console.log("5. Actualización de UI completada con el nuevo umbral:", umbralNum);
    });
  }
  
  // Inicializar buscador
  const searchInput = document.getElementById('pos-search');
  if (searchInput) {
    searchInput.addEventListener('input', function() {
      filterProducts(this.value);
    });
  }
  
  // Evento para botón Listo
  readyBtn.addEventListener('click', () => {
    if (!cart.length) return alert('El carrito está vacío');
    document.querySelectorAll('.product-btn').forEach(b => b.disabled = true);
    paymentSelect.disabled = false;
    readyBtn.disabled = true;
    checkoutBtn.disabled = false; // Explícitamente habilitamos el botón de cobrar
    
    // Aseguramos que el botón de checkout esté habilitado
    setTimeout(() => {
      checkoutBtn.disabled = false;
      console.log("Botón de cobrar habilitado: ", checkoutBtn.disabled);
    }, 100);
  });
  
  // Evento para botón Checkout
  checkoutBtn.addEventListener('click', async () => {
    // Calcular subtotal y descuento para enviar
    let subtotal = 0;
    let descuentoTotal = 0;
    
    // Calcular subtotal y descuentos por producto
    cart.forEach(item => {
      subtotal += item.precio_unitario * item.cantidad;
      if (discountMode === 'item' && item.descuento) {
        descuentoTotal += item.descuento;
      }
    });
    
    // Si el modo de descuento es total, calcular el descuento general
    if (discountMode === 'total' && discountPercentage > 0) {
      descuentoTotal = calculateDiscount(subtotal, discountPercentage);
    }
    
    const payload = {
      items: cart.map(i => ({ 
        producto_id: i.producto_id, 
        cantidad: i.cantidad,
        descuento: discountMode === 'item' ? i.descuento || 0 : 0
      })),
      metodo_pago: paymentSelect.value,
      subtotal: subtotal,
      descuento: descuentoTotal,
      descuento_porcentaje: discountMode === 'total' ? discountPercentage : 0
    };
    const res = await fetch('/pos/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      
      // Mensaje más detallado con información de descuento
      let message = `✅ Orden #${data.id} registrada\n`;
      if (descuentoTotal > 0) {
        message += `Subtotal: ${formatCurrency(subtotal)}\n`;
        message += `Descuento: -${formatCurrency(descuentoTotal)}\n`;
      }
      message += `Total: ${formatCurrency(data.total)}`;
      
      alert(message);
      
      // Resetear carrito y descuentos
      cart = [];
      discountPercentage = 0;
      selectedItemForDiscount = null;
      renderCart();
      loadProducts();
    } else {
      const err = await res.json();
      alert(`❌ ${err.detail}`);
    }
  });
  
  // Evento para botón Limpiar
  clearBtn.addEventListener('click', () => {
    if (!cart.length) return;
    if (confirm('¿Limpiar todo el carrito?')) {
      // Restaurar stock disponible de todos los productos en el carrito
      cart.forEach(item => {
        stockDisponible[item.producto_id] += item.cantidad;
      });
      
      // Resetear descuentos
      discountPercentage = 0;
      selectedItemForDiscount = null;
      
      // Actualizar botones y visualización de stock
      document.querySelectorAll('.product-btn').forEach(btn => {
        const id = btn.dataset.id;
        if (stockDisponible[id] > 0) {
          btn.disabled = false;
          const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
          actualizarVisualizacionStock(stockDisplay, stockDisponible[id]);
        }
      });
      
      // Vaciar carrito
      cart = [];
      renderCart();
      
      paymentSelect.disabled = true;
      readyBtn.disabled = true;
      checkoutBtn.disabled = true;
    }
  });
  
  // Botones de porcentaje de descuento
  discountBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const percentage = parseInt(btn.dataset.discount, 10);
      discountPercentage = percentage;
      
      // Actualizar estado visual de los botones
      discountBtns.forEach(b => b.classList.remove('bg-blue-200', 'dark:bg-blue-800', 'text-blue-800', 'dark:text-blue-300'));
      btn.classList.add('bg-blue-200', 'dark:bg-blue-800', 'text-blue-800', 'dark:text-blue-300');
      
      applyDiscount();
    });
  });
  
  // Descuento personalizado
  customDiscountBtn.addEventListener('click', () => {
    const userInput = prompt("Ingrese el porcentaje de descuento (1-99):", discountPercentage || "");
    if (userInput === null) return; // Cancelado
    
    const percentage = parseInt(userInput, 10);
    if (isNaN(percentage) || percentage < 1 || percentage > 99) {
      alert("Por favor ingrese un valor válido entre 1 y 99");
      return;
    }
    
    discountPercentage = percentage;
    
    // Actualizar estado visual de los botones
    discountBtns.forEach(b => b.classList.remove('bg-blue-200', 'dark:bg-blue-800', 'text-blue-800', 'dark:text-blue-300'));
    customDiscountBtn.classList.add('bg-blue-200', 'dark:bg-blue-800', 'text-blue-800', 'dark:text-blue-300');
    customDiscountBtn.textContent = `${percentage}%`;
    
    applyDiscount();
  });
  
  // Resetear descuento
  resetDiscountBtn.addEventListener('click', () => {
    discountPercentage = 0;
    selectedItemForDiscount = null;
    
    // Resetear estado visual de los botones
    discountBtns.forEach(b => b.classList.remove('bg-blue-200', 'dark:bg-blue-800', 'text-blue-800', 'dark:text-blue-300'));
    customDiscountBtn.textContent = 'Custom';
    
    applyDiscount();
  });
  
  // Cambiar entre modo de descuento total o por producto
  discountTotalBtn.addEventListener('click', () => {
    discountMode = 'total';
    discountTotalBtn.classList.add('active', 'bg-blue-100', 'hover:bg-blue-200', 'text-blue-800', 'dark:bg-blue-900/50', 'dark:hover:bg-blue-800', 'dark:text-blue-300');
    discountItemBtn.classList.remove('active', 'bg-blue-100', 'hover:bg-blue-200', 'text-blue-800', 'dark:bg-blue-900/50', 'dark:hover:bg-blue-800', 'dark:text-blue-300');
    discountItemBtn.classList.add('bg-gray-200', 'hover:bg-gray-300', 'dark:bg-gray-700', 'dark:hover:bg-gray-600');
    
    applyDiscount();
  });
  
  discountItemBtn.addEventListener('click', () => {
    discountMode = 'item';
    discountItemBtn.classList.add('active', 'bg-blue-100', 'hover:bg-blue-200', 'text-blue-800', 'dark:bg-blue-900/50', 'dark:hover:bg-blue-800', 'dark:text-blue-300');
    discountTotalBtn.classList.remove('active', 'bg-blue-100', 'hover:bg-blue-200', 'text-blue-800', 'dark:bg-blue-900/50', 'dark:hover:bg-blue-800', 'dark:text-blue-300');
    discountTotalBtn.classList.add('bg-gray-200', 'hover:bg-gray-300', 'dark:bg-gray-700', 'dark:hover:bg-gray-600');
    
    applyDiscount();
  });
  
  // Funcionalidad de modo oscuro
  const themeToggleBtn = document.getElementById('theme-toggle');
  const themeToggleDarkIcon = document.getElementById('theme-toggle-dark-icon');
  const themeToggleLightIcon = document.getElementById('theme-toggle-light-icon');

  // Cambiar iconos según el tema actual
  if (localStorage.getItem('color-theme') === 'dark' || (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      themeToggleLightIcon.classList.remove('hidden');
      document.documentElement.classList.add('dark');
  } else {
      themeToggleDarkIcon.classList.remove('hidden');
      document.documentElement.classList.remove('dark');
  }

  // Listener para el toggle de tema
  themeToggleBtn.addEventListener('click', function() {
      // Toggle iconos
      themeToggleDarkIcon.classList.toggle('hidden');
      themeToggleLightIcon.classList.toggle('hidden');

      // Si ya hay theme en localStorage
      if (localStorage.getItem('color-theme')) {
          if (localStorage.getItem('color-theme') === 'light') {
              document.documentElement.classList.add('dark');
              localStorage.setItem('color-theme', 'dark');
          } else {
              document.documentElement.classList.remove('dark');
              localStorage.setItem('color-theme', 'light');
          }
      } else {
          if (document.documentElement.classList.contains('dark')) {
              document.documentElement.classList.remove('dark');
              localStorage.setItem('color-theme', 'light');
          } else {
              document.documentElement.classList.add('dark');
              localStorage.setItem('color-theme', 'dark');
          }
      }
  });
  
  // Iniciar la carga de productos
  loadProducts();
  renderCart();
  
  // Actualizar stock cada minuto para mantenerlo sincronizado
  setInterval(actualizarStockEnTiempoReal, 60000);
  
  // Actualizar cuando el usuario vuelve a la página
  document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
      actualizarStockEnTiempoReal();
    }
  });
  
  console.log("POS System inicializado correctamente");
  
  // Escuchar cambios en localStorage (incluso de otras pestañas)
  window.addEventListener('storage', function(event) {
    if (event.key === 'stockUmbralPOS') {
      console.log(`Detectado cambio en localStorage: ${event.oldValue} -> ${event.newValue}`);
      
      const nuevoUmbral = parseInt(event.newValue, 10);
      if (!isNaN(nuevoUmbral) && nuevoUmbral >= 1) {
        stockUmbral = nuevoUmbral;
        
        // Actualizar el UI
        const umbralActualEl = document.getElementById('umbral-actual');
        if (umbralActualEl) {
          umbralActualEl.textContent = stockUmbral;
        }
        
        // Actualizar visualización de todos los productos
        document.querySelectorAll('.product-btn').forEach(btn => {
          const id = parseInt(btn.dataset.id);
          const stockActual = parseInt(btn.dataset.stock, 10);
          
          // Actualizar texto de stock
          const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
          actualizarVisualizacionStock(stockDisplay, stockActual);
        });
      }
    }
  });
});

// También actualizamos todos los productos cuando cambia el umbral manualmente
function actualizarVisualizacionTodosProductos() {
  console.log("Actualizando visualización de todos los productos con umbral:", stockUmbral);
  
  document.querySelectorAll('.product-btn').forEach(btn => {
    const id = parseInt(btn.dataset.id);
    const stockActual = parseInt(btn.dataset.stock, 10);
    
    // Actualizar texto de stock
    const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
    actualizarVisualizacionStock(stockDisplay, stockActual);
  });
}

// Exponer funciones que se llaman desde HTML
window.addToCart = addToCart;
window.removeFromCart = removeFromCart;
window.selectItemForDiscount = selectItemForDiscount;
