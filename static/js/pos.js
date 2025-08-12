// Variables globales
let cart = [];
let discountPercentage = 0;
let discountMode = 'total'; // 'total' o 'item'
let selectedItemForDiscount = null;
let allProducts = [];
let searchCache = new Map(); // Cache para búsquedas recientes
let cacheTimeout = 30000; // 30 segundos de cache

// Monitor de performance (universal o específico)
const getPerformanceMonitor = () => {
  return window.universalMonitor || window.performanceMonitor || { 
    measureAsync: async (name, fn) => fn(), 
    measure: (name, fn) => fn() 
  };
};
(function(){
  let stockUmbral = 5;
  const stockDisponible = {}; // id -> cantidad disponible

  // DOM
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
  const categoryFilter = document.getElementById('category-filter');
  const searchInput = document.getElementById('pos-search');

  // Utils
  function formatCurrency(amount){
    return new Intl.NumberFormat('es-CL',{style:'currency',currency:'CLP',minimumFractionDigits:0}).format(amount||0);
  }
  
  function showError(message) {
    const errorEl = document.createElement('div');
    errorEl.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md z-50';
    errorEl.textContent = message;
    document.body.appendChild(errorEl);
    
    setTimeout(() => {
      if (errorEl.parentNode) {
        errorEl.parentNode.removeChild(errorEl);
      }
    }, 5000);
  }
  
  function getUmbral(){
    const val = parseInt(localStorage.getItem('stockUmbralPOS')||'5',10);
    stockUmbral = (!isNaN(val) && val>=1)? val : 5;
    const el = document.getElementById('umbral-actual');
    if (el) el.textContent = stockUmbral;
    return stockUmbral;
  }
  function setUmbral(newVal){
    stockUmbral = newVal; localStorage.setItem('stockUmbralPOS', String(newVal));
    const el = document.getElementById('umbral-actual');
    if (el) el.textContent = stockUmbral;
    actualizarVisualizacionTodosProductos();
  }

  // Data - Versión optimizada con paginación y búsqueda
  async function fetchProducts(searchTerm = '', page = 0, limit = 50){
    return await getPerformanceMonitor().measureAsync(`fetchProducts(${searchTerm ? 'search' : 'load'}, page=${page})`, async () => {
      const params = new URLSearchParams();
      if (searchTerm.trim()) params.append('q', searchTerm.trim());
      params.append('skip', page * limit);
      params.append('limit', limit);
      
      const url = `/pos/products?${params.toString()}`;
      const res = await fetch(url);
      if(!res.ok) throw new Error('No se pudieron cargar productos (HTTP '+res.status+')');
      const prods = await res.json();
      
      // Si es la primera página, reiniciar allProducts, sino concatenar
      if (page === 0) {
        allProducts = Array.isArray(prods) ? prods : [];
      } else {
        allProducts = allProducts.concat(Array.isArray(prods) ? prods : []);
      }
      
      try { window.allProducts = allProducts; } catch {}
      
      // ⚡ FIX: actualizar stockDisponible respetando carrito local
      prods.forEach(p=>{
        if (p && typeof p.id !== 'undefined') {
          const serverStock = Number.isFinite(p.cantidad) ? p.cantidad : 0;
          const inCart = cart.filter(item => item.producto_id === p.id)
                            .reduce((total, item) => total + item.cantidad, 0);
          
          // Solo actualizar si no hay productos en carrito, o ajustar según carrito
          if (inCart === 0) {
            stockDisponible[p.id] = serverStock;
          } else {
            const expectedLocalStock = serverStock - inCart;
            stockDisponible[p.id] = Math.max(0, expectedLocalStock);
          }
        }
      });
      
      return prods;
    });
  }

  // Búsqueda rápida optimizada para autocompletado con cache
  async function searchProductsFast(searchTerm, limit = 20) {
    if (!searchTerm.trim()) return [];
    
    const cacheKey = `${searchTerm.trim()}_${limit}`;
    
    // Verificar cache
    if (searchCache.has(cacheKey)) {
      const cached = searchCache.get(cacheKey);
      if (Date.now() - cached.timestamp < cacheTimeout) {
        return cached.data;
      } else {
        searchCache.delete(cacheKey);
      }
    }
    
    const params = new URLSearchParams();
    params.append('q', searchTerm.trim());
    params.append('limit', limit);
    
    const res = await fetch(`/pos/search?${params.toString()}`);
    if(!res.ok) throw new Error('Error en búsqueda rápida');
    
    const results = await res.json();
    
    // ⚡ FIX: Actualizar stockDisponible con los resultados de búsqueda
    console.log('🔍 Actualizando stock desde búsqueda:', results.length, 'productos');
    results.forEach(p => {
      if (p && typeof p.id !== 'undefined') {
        const oldStock = stockDisponible[p.id] || 0;
        const serverStock = Number.isFinite(p.cantidad) ? p.cantidad : 0;
        
        // ⚡ FIX: Calcular stock en carrito para mantener consistencia
        const inCart = cart.filter(item => item.producto_id === p.id)
                          .reduce((total, item) => total + item.cantidad, 0);
        
        // Solo actualizar si no hay cambios locales (carrito vacío para este producto)
        if (inCart === 0) {
          stockDisponible[p.id] = serverStock;
          console.log(`📦 Producto ${p.id} (${p.nombre}): stock ${oldStock} → ${serverStock} (sin carrito)`);
        } else {
          // Mantener el stock local pero verificar consistencia
          const expectedLocalStock = serverStock - inCart;
          if (expectedLocalStock >= 0) {
            stockDisponible[p.id] = expectedLocalStock;
            console.log(`📦 Producto ${p.id} (${p.nombre}): stock ajustado a ${expectedLocalStock} (servidor: ${serverStock}, carrito: ${inCart})`);
          } else {
            console.warn(`⚠️ Producto ${p.id}: stock insuficiente en servidor (${serverStock}) vs carrito (${inCart})`);
          }
        }
        
        // ⚡ FIX: Agregar productos de búsqueda a allProducts si no existen
        const existingIndex = allProducts.findIndex(existing => existing.id === p.id);
        if (existingIndex >= 0) {
          // Actualizar producto existente
          allProducts[existingIndex] = p;
        } else {
          // Agregar nuevo producto
          allProducts.push(p);
          console.log(`➕ Producto ${p.id} agregado a allProducts`);
        }
      }
    });
    
    // Actualizar referencia global
    try { window.allProducts = allProducts; } catch {}
    
    // Guardar en cache
    searchCache.set(cacheKey, {
      data: results,
      timestamp: Date.now()
    });
    
    // Limpiar cache viejo si es muy grande
    if (searchCache.size > 50) {
      const oldest = Array.from(searchCache.entries())
        .sort((a, b) => a[1].timestamp - b[1].timestamp)[0];
      searchCache.delete(oldest[0]);
    }
    
    return results;
  }

  // Cargar productos iniciales (solo los primeros 30 para velocidad)
  async function loadInitialProducts() {
    try {
      await fetchProducts('', 0, 100); // Cargar más productos para ver todas las categorías
      populateCategories();
      renderProducts(allProducts);
    } catch (error) {
      console.error('Error cargando productos iniciales:', error);
      showError('Error cargando productos. Intenta recargar la página.');
    }
  }

  // Función para mostrar errores de forma amigable
  function showError(message) {
    if (productsSection) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4';
      errorDiv.innerHTML = `
        <div class="flex items-center">
          <span class="text-red-500 mr-2">⚠️</span>
          <span>${message}</span>
        </div>
      `;
      productsSection.prepend(errorDiv);
      
      // Remover error después de 5 segundos
      setTimeout(() => errorDiv.remove(), 5000);
    }
  }

  function groupByCategory(list){
    const out = {};
    list.forEach(p=>{
      const cat = (p.categoria && p.categoria.nombre) || 'Otros';
      if(!out[cat]) out[cat] = [];
      out[cat].push(p);
    });
    return out;
  }

  function populateCategories(){
    if (!categoryFilter) return;
    const current = categoryFilter.value;
    const head = document.createElement('option');
    head.value = '';
    head.textContent = 'Todas las categorías';
    const names = Array.from(new Set(allProducts.map(p=> (p.categoria && p.categoria.nombre) || 'Otros'))).sort();
    categoryFilter.innerHTML = '';
    categoryFilter.appendChild(head);
    names.forEach(name=>{
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      categoryFilter.appendChild(opt);
    });
    if (names.includes(current)) categoryFilter.value = current; else categoryFilter.value = '';
  }

  // Render
  function stockHtmlFor(id){
    const s = stockDisponible[id]||0;
    if (s<=0) return '<span class="text-red-500">Sin stock</span>';
    if (s<=stockUmbral) return `<span class="text-amber-500">Stock bajo: ${s}</span>`;
    return `Stock: ${s}`;
  }

  function renderProducts(list){
    if (!productsSection) return;
    productsSection.innerHTML = '';
    if (!list || list.length === 0){
      const empty = document.createElement('div');
      empty.className = 'text-sm text-gray-500 dark:text-gray-400 p-4';
      empty.textContent = 'No hay productos para mostrar.';
      productsSection.appendChild(empty);
      return;
    }
    const byCat = groupByCategory(list);
    const categories = Object.keys(byCat).sort();
    categories.forEach(cat=>{
      const section = document.createElement('section');
      section.className = 'space-y-4';
      section.innerHTML = `
        <h2 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">${cat}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3"></div>
      `;
      const grid = section.querySelector('div');
      byCat[cat].forEach(p=>{
        const stock = stockDisponible[p.id]||0;
        const btn = document.createElement('button');
        btn.className = 'product-btn group text-left';
        btn.dataset.id = p.id;
        btn.dataset.price = p.precio;
        btn.dataset.name = p.nombre;
        btn.dataset.stock = stock;
        btn.disabled = stock<=0;
        btn.innerHTML = `
          <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 transition-all duration-200 ${stock<=0?'opacity-50 cursor-not-allowed':'hover:shadow-md hover:border-sage-300 dark:hover:border-sage-600'}">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-medium text-gray-900 dark:text-gray-100">${p.nombre}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">${formatCurrency(p.precio)}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 stock-display" data-id="${p.id}">${stockHtmlFor(p.id)}</p>
              </div>
              <div class="w-8 h-8 bg-sage-100 dark:bg-sage-800 rounded-full flex items-center justify-center ${stock>0?'group-hover:bg-sage-200 dark:group-hover:bg-sage-700':''} transition-colors duration-200">
                <svg class="w-4 h-4 text-sage-600 dark:text-sage-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"/>
                </svg>
              </div>
            </div>
          </div>
        `;
        btn.addEventListener('click', ()=> addToCart(p.id, p.nombre, p.precio));
        grid.appendChild(btn);
      });
      productsSection.appendChild(section);
    });
  }

  function actualizarVisualizacionTodosProductos(){
    document.querySelectorAll('.product-btn').forEach(btn=>{
      const id = parseInt(btn.dataset.id,10);
      const stock = stockDisponible[id]||0;
      const hasStock = stock > 0;
      
      // Actualizar estado del botón
      btn.disabled = !hasStock;
      btn.dataset.stock = stock;
      
      // ⚡ FIX: Actualizar clases CSS visuales del contenedor interno
      const innerDiv = btn.querySelector('div');
      if (innerDiv) {
        // Remover clases anteriores
        innerDiv.classList.remove('opacity-50', 'cursor-not-allowed', 'hover:shadow-md', 'hover:border-sage-300', 'dark:hover:border-sage-600');
        
        // Aplicar clases según stock
        if (hasStock) {
          innerDiv.classList.add('hover:shadow-md', 'hover:border-sage-300', 'dark:hover:border-sage-600');
        } else {
          innerDiv.classList.add('opacity-50', 'cursor-not-allowed');
        }
      }
      
      // ⚡ FIX: Actualizar clases del icono de agregar
      const iconContainer = btn.querySelector('.w-8.h-8');
      if (iconContainer) {
        // Remover clases anteriores del hover
        iconContainer.classList.remove('group-hover:bg-sage-200', 'dark:group-hover:bg-sage-700');
        
        // Aplicar hover solo si hay stock
        if (hasStock) {
          iconContainer.classList.add('group-hover:bg-sage-200', 'dark:group-hover:bg-sage-700');
        }
      }
      
      // Actualizar display de stock
      const stockDisplay = document.querySelector(`.stock-display[data-id="${id}"]`);
      if (stockDisplay) stockDisplay.innerHTML = stockHtmlFor(id);
      
      console.log(`🔄 Producto ${id}: stock=${stock}, disabled=${!hasStock}, clases actualizadas`);
    });
  }

  // Carrito
  function renderCart(){
    cartItemsEl.innerHTML = '';
    if (!cart.length){
      cartItemsEl.appendChild(emptyCartEl);
      cartTotalEl.textContent = formatCurrency(0);
      cartDiscountEl.textContent = formatCurrency(0);
      return;
    }
    if (emptyCartEl.parentNode) emptyCartEl.remove();

    let subtotal = 0, descuento = 0;
    cart.forEach(item=>{
      const itemTotal = item.precio_unitario * item.cantidad;
      subtotal += itemTotal;
      if (discountMode==='item' && item.descuento) descuento += item.descuento;

      const el = document.createElement('div');
      el.className = 'flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg cart-item';
      el.dataset.id = item.producto_id;
      el.innerHTML = `
        <div class="flex items-center space-x-3">
          <button class="w-6 h-6 bg-red-100 dark:bg-red-800 hover:bg-red-200 dark:hover:bg-red-700 text-red-600 dark:text-red-200 rounded-full flex items-center justify-center text-sm font-medium" onclick="removeFromCart(${item.producto_id})">−</button>
          <div>
            <p class="font-medium text-gray-900 dark:text-gray-100 text-sm">${item.nombre}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">x${item.cantidad} @ ${formatCurrency(item.precio_unitario)}</p>
          </div>
        </div>
        <div class="text-right">
          <span class="font-medium text-gray-900 dark:text-gray-100">${formatCurrency(itemTotal)}</span>
        </div>
      `;
      cartItemsEl.appendChild(el);
    });

    if (discountMode==='total' && discountPercentage>0){
      descuento = Math.round(subtotal * (discountPercentage/100));
    }
    const total = subtotal - descuento;
    cartDiscountEl.textContent = formatCurrency(descuento);
    cartTotalEl.textContent = formatCurrency(total);
  }

  function updateCartState(){
    const has = cart.length>0;
    readyBtn.disabled = !has;
    checkoutBtn.disabled = paymentSelect.disabled;
  }

  function addToCart(id, name, price){
    const currentStock = stockDisponible[id] || 0;
    if (currentStock <= 0) {
      console.warn(`❌ Intento agregar producto ${id} (${name}) sin stock disponible`);
      return alert('No hay suficiente stock disponible');
    }
    
    // Reducir stock disponible
    stockDisponible[id] = currentStock - 1;
    
    // Agregar al carrito
    const existingItem = cart.find(x => x.producto_id === id);
    if (existingItem) {
      existingItem.cantidad++;
    } else {
      cart.push({producto_id: id, nombre: name, precio_unitario: price, cantidad: 1});
    }
    
    console.log(`🛒➕ Producto ${id} (${name}): agregado, stock ${currentStock} → ${stockDisponible[id]}`);
    
    actualizarVisualizacionTodosProductos();
    renderCart(); 
    updateCartState();
  }
  function removeFromCart(id){
    const idx = cart.findIndex(x=>x.producto_id===id);
    if (idx<0) return;
    
    const removedQuantity = 1;
    const productName = cart[idx].nombre;
    
    cart[idx].cantidad--;
    if (cart[idx].cantidad<=0) cart.splice(idx,1);
    
    // Devolver stock
    const oldStock = stockDisponible[id] || 0;
    stockDisponible[id] = oldStock + removedQuantity;
    const newStock = stockDisponible[id];
    
    console.log(`🛒➖ Producto ${id} (${productName}): removido 1, stock ${oldStock} → ${newStock}`);
    
    actualizarVisualizacionTodosProductos();
    renderCart(); 
    updateCartState();
  }

  // Filtros optimizados con debounce y búsqueda en servidor
  let searchTimeout = null;
  let isSearching = false;
  
  function showSearchIndicator() {
    if (!productsSection) return;
    if (!isSearching) {
      isSearching = true;
      const indicator = document.createElement('div');
      indicator.id = 'search-indicator';
      indicator.className = 'text-center py-4 text-sm text-gray-500';
      indicator.innerHTML = '🔍 Buscando productos...';
      productsSection.prepend(indicator);
    }
  }
  
  function hideSearchIndicator() {
    isSearching = false;
    const indicator = document.getElementById('search-indicator');
    if (indicator) indicator.remove();
  }
  
  async function applyFilters(){
    const q = (searchInput?.value||'').trim();
    const cat = categoryFilter?.value||'';
    
    // Si hay búsqueda por texto, usar la API rápida
    if (q && q.length >= 1) {
      showSearchIndicator();
      try {
        const searchResults = await searchProductsFast(q, 30);
        let filteredResults = searchResults;
        
        // Aplicar filtro de categoría si es necesario
        if (cat) {
          filteredResults = searchResults.filter(p => {
            const name = (p.categoria && p.categoria.nombre) || 'Otros';
            return name === cat;
          });
        }
        
        hideSearchIndicator();
        renderProducts(filteredResults);
        return;
      } catch (error) {
        hideSearchIndicator();
        console.error('Error en búsqueda rápida:', error);
        // Fallback a búsqueda local si falla la búsqueda en servidor
      }
    } else {
      hideSearchIndicator();
    }
    
    // Filtrado local para categorías o búsquedas vacías
    let list = allProducts;
    
    if (q) {
      list = list.filter(p => 
        (p.nombre||'').toLowerCase().includes(q.toLowerCase()) ||
        ((p.codigo_barras||'').toLowerCase().includes(q.toLowerCase())) ||
        (((p.categoria&&p.categoria.nombre)||'').toLowerCase().includes(q.toLowerCase()))
      );
    }
    
    if (cat) {
      list = list.filter(p => {
        const name = (p.categoria && p.categoria.nombre) || 'Otros';
        return name === cat;
      });
    }
    
    renderProducts(list);
  }
  
  // Función con debounce para búsqueda
  function debouncedSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(applyFilters, 200); // Reducido a 200ms para mejor UX
  }

  // Inicialización principal
  async function init(){
    // Umbral inicial
    getUmbral();

    // Config umbral botón
    const cfgBtn = document.getElementById('config-stock-btn');
    if (cfgBtn){
      cfgBtn.addEventListener('click', ()=>{
        const input = prompt('Ingrese el umbral para considerar stock bajo (1-100):', String(stockUmbral));
        if (input===null) return;
        const n = parseInt(input,10);
        if (isNaN(n)||n<1||n>100) return alert('Valor inválido');
        setUmbral(n);
      });
    }

    // Cargar productos iniciales optimizado
    try {
      console.debug('[POS] Cargando productos iniciales...');
      await loadInitialProducts();
      console.debug(`[POS] Productos cargados: ${allProducts.length}`);
    } catch (e) {
      console.error('Error cargando productos', e);
      if (productsSection){
        productsSection.innerHTML = '';
        const err = document.createElement('div');
        err.className = 'text-sm text-red-600 dark:text-red-400 p-4';
        err.textContent = 'Error cargando productos. Revise la consola del navegador.';
        productsSection.appendChild(err);
      }
    }

    // Search optimizado con debounce y categoría
    if (searchInput) searchInput.addEventListener('input', debouncedSearch);
    if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);

    // Ready / Checkout / Clear
    readyBtn.addEventListener('click', ()=>{
      if (!cart.length) return alert('El carrito está vacío');
      document.querySelectorAll('.product-btn').forEach(b=>b.disabled=true);
      paymentSelect.disabled = false;
      readyBtn.disabled = true;
      checkoutBtn.disabled = false;
    });

    checkoutBtn.addEventListener('click', async ()=>{
      if (!cart.length) return alert('El carrito está vacío');
      let subtotal = 0; cart.forEach(i=> subtotal += i.precio_unitario*i.cantidad);
      const descuentoTotal = (discountMode==='total' && discountPercentage>0) ? Math.round(subtotal*(discountPercentage/100)) : 0;
      const payload = {
        items: cart.map(i=>({producto_id:i.producto_id, cantidad:i.cantidad, descuento: discountMode==='item' ? (i.descuento||0):0})),
        metodo_pago: paymentSelect.value,
        subtotal: subtotal,
        descuento: descuentoTotal,
        descuento_porcentaje: discountMode==='total'?discountPercentage:0
      };
      const res = await fetch('/pos/order',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)});
      if (res.ok){
        const data = await res.json();
        alert(`✅ Orden #${data.id} registrada\nTotal: ${formatCurrency(data.total)}`);
        // Reset UI
        cart = []; renderCart();
        paymentSelect.disabled = true; readyBtn.disabled = true; checkoutBtn.disabled = true;
        document.querySelectorAll('.product-btn').forEach(b=>b.disabled=false);
        await fetchProducts(); populateCategories(); renderProducts(allProducts);
      } else {
        const err = await res.json().catch(()=>({detail:'Error en checkout'}));
        alert(`❌ ${err.detail||'Error en checkout'}`);
      }
    });

    clearBtn.addEventListener('click', ()=>{
      if (!cart.length) return;
      if (!confirm('¿Limpiar todo el carrito?')) return;
      
      // ⚡ FIX: Devolver stock al limpiar carrito pero respetar límites reales
      cart.forEach(item => {
        const currentStock = stockDisponible[item.producto_id] || 0;
        stockDisponible[item.producto_id] = currentStock + item.cantidad;
      });
      
      cart = []; 
      renderCart(); 
      actualizarVisualizacionTodosProductos(); // Esto respetará el stock real
      paymentSelect.disabled = true; 
      readyBtn.disabled = true; 
      checkoutBtn.disabled = true;
      
      // ⚡ FIX: No forzar todos los botones enabled - dejar que actualizarVisualizacionTodosProductos maneje el estado
      console.log('🧹 Carrito limpiado, stock restaurado');
    });

    // Descuentos básicos
    discountBtns.forEach(btn=>{
      btn.addEventListener('click', ()=>{
        const p = parseInt(btn.dataset.discount,10);
        discountPercentage = isNaN(p)?0:p;
        discountBtns.forEach(b=> b.classList.remove('bg-blue-200','dark:bg-blue-800','text-blue-800','dark:text-blue-300'));
        btn.classList.add('bg-blue-200','dark:bg-blue-800','text-blue-800','dark:text-blue-300');
        renderCart();
      });
    });
    customDiscountBtn.addEventListener('click', ()=>{
      const u = prompt('Ingrese el porcentaje de descuento (1-99):', String(discountPercentage||''));
      if (u===null) return; const p = parseInt(u,10);
      if (isNaN(p)||p<1||p>99) return alert('Valor inválido');
      discountPercentage = p; renderCart();
    });
    resetDiscountBtn.addEventListener('click', ()=>{ discountPercentage=0; renderCart(); });
    discountTotalBtn.addEventListener('click', ()=>{ discountMode='total'; renderCart(); });
    discountItemBtn.addEventListener('click', ()=>{ discountMode='item'; renderCart(); });

    // Exponer funciones globales para el lector de códigos
    window.addToCart = addToCart;
    window.removeFromCart = removeFromCart;
    window.allProducts = allProducts;
    
    // ⚡ FIX: Función para sincronizar stock cuando el escáner carga productos
    window.syncStockForProducts = function(products) {
      console.log('🔄 Sincronizando stock para productos del escáner:', products.length);
      products.forEach(p => {
        if (p && typeof p.id !== 'undefined') {
          const serverStock = Number.isFinite(p.cantidad) ? p.cantidad : 0;
          const inCart = cart.filter(item => item.producto_id === p.id)
                            .reduce((total, item) => total + item.cantidad, 0);
          
          // Solo actualizar si no hay productos en carrito para este producto
          if (inCart === 0) {
            stockDisponible[p.id] = serverStock;
          } else {
            const expectedLocalStock = serverStock - inCart;
            stockDisponible[p.id] = Math.max(0, expectedLocalStock);
          }
          
          console.log(`📦 Stock sincronizado: Producto ${p.id} = ${stockDisponible[p.id]} (servidor: ${serverStock}, carrito: ${inCart})`);
        }
      });
      
      // Actualizar visualización si es necesario
      actualizarVisualizacionTodosProductos();
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    // DOM ya cargado
    init();
  }
})();

// Modo oscuro: inicialización de íconos y toggle seguro
document.addEventListener('DOMContentLoaded', ()=>{
  const btn = document.getElementById('theme-toggle');
  const darkIcon = document.getElementById('theme-toggle-dark-icon');
  const lightIcon = document.getElementById('theme-toggle-light-icon');
  if (!btn || !darkIcon || !lightIcon) return; // No romper si no existe

  function setIcons(){
    const isDark = document.documentElement.classList.contains('dark');
    // Si está en oscuro, mostramos el icono de sol (para pasar a claro)
    lightIcon.classList.toggle('hidden', !isDark);
    darkIcon.classList.toggle('hidden', isDark);
  }

  // Estado inicial
  const userPref = localStorage.getItem('color-theme');
  const shouldDark = userPref === 'dark' || (!userPref && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('dark', !!shouldDark);
  setIcons();

  btn.addEventListener('click', ()=>{
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('color-theme', isDark ? 'dark' : 'light');
    setIcons();
  });
});