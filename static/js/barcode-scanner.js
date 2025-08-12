// barcode-scanner.js
// Soporte ligero para lectores de código de barras tipo HID (emulan teclado)
// Modo: captura teclas rápidas y Enter para disparar acción.
// Requiere: input#pos-search, funciones/elementos de POS ya existentes.

(function(){
  let buffer = '';
  let lastTs = 0;
  const MAX_DELAY = 50; // ms entre teclas para considerar "scanner"
  const MIN_LENGTH = 6; // longitud mínima de código de barras típica

  const searchInput = document.getElementById('pos-search');
  const statusEl = document.getElementById('scanner-status');
  const enabledEl = document.getElementById('scanner-enabled');
  const autoAddEl = document.getElementById('scanner-auto-add');

  // Persistencia sencilla en localStorage
  const KEY_ENABLED = 'posScannerEnabled';
  const KEY_AUTOADD = 'posScannerAutoAdd';

  function setStatus(text, ok){
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.classList.toggle('text-green-600', !!ok);
    statusEl.classList.toggle('dark:text-green-400', !!ok);
  }

  function readPrefs(){
    try {
      const en = localStorage.getItem(KEY_ENABLED);
      const aa = localStorage.getItem(KEY_AUTOADD);
      if (enabledEl) enabledEl.checked = en === '1';
      if (autoAddEl) autoAddEl.checked = aa === '1';
      setStatus(enabledEl && enabledEl.checked ? 'Escáner activo' : 'Escáner inactivo', enabledEl && enabledEl.checked);
    } catch {}
  }

  function savePrefs(){
    try {
      if (enabledEl) localStorage.setItem(KEY_ENABLED, enabledEl.checked ? '1' : '0');
      if (autoAddEl) localStorage.setItem(KEY_AUTOADD, autoAddEl.checked ? '1' : '0');
    } catch {}
  }

  function isScannerKeyEvent(e){
    // Ignorar si se está escribiendo en un input/textarea (excepto el buscador)
    const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
    const isTyping = tag === 'input' || tag === 'textarea';
    if (isTyping && e.target !== searchInput) return false;

    const now = Date.now();
    const fast = now - lastTs <= MAX_DELAY;
    lastTs = now;
    // Si es rápido y es una tecla alfanumérica o separadores comunes del lector
    const k = e.key;
    const candidate = k.length === 1 || k === 'Enter' || k === 'Tab';
    return fast && candidate;
  }

  function getAllProducts(){
    try {
      // Preferir variable global si existe (top-level let no es propiedad de window)
      // eslint-disable-next-line no-undef
      if (typeof allProducts !== 'undefined' && Array.isArray(allProducts)) return allProducts;
    } catch {}
    return (window.allProducts && Array.isArray(window.allProducts)) ? window.allProducts : [];
  }

  async function ensureProducts(){
    const list = getAllProducts();
    if (list.length) return list;
    try {
      const res = await fetch('/pos/products?limit=200'); // Cargar más productos para tener mejor coverage
      if (!res.ok) return [];
      const data = await res.json();
      
      // ⚡ FIX: Sincronizar stockDisponible cuando cargamos productos para escáner
      if (Array.isArray(data) && data.length > 0) {
        // Acceder al objeto stockDisponible global si existe
        try {
          // Verificar si hay una función global para sincronizar stock
          if (typeof window.syncStockForProducts === 'function') {
            window.syncStockForProducts(data);
          } else {
            // Fallback: intentar acceder directamente (esto puede no funcionar por scope)
            console.log('🔄 Productos cargados para escáner:', data.length);
          }
        } catch (e) {
          console.warn('No se pudo sincronizar stock automáticamente:', e);
        }
      }
      
      try { window.allProducts = data; } catch {}
      return Array.isArray(data) ? data : [];
    } catch { return []; }
  }

  async function handleScanned(code){
    if (!code || code.length < MIN_LENGTH) return;
    
    // 1) Poner el foco y setear el buscador
    if (searchInput) {
      searchInput.focus();
      searchInput.value = code;
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // 2) Intentar agregar al carrito automáticamente si está activo
    const autoAdd = autoAddEl && autoAddEl.checked;
    if (autoAdd) {
      try {
        // ⚡ FIX: Asegurar productos y sincronizar stock antes de buscar
        let prods = await ensureProducts();
        
        // Buscar primero localmente
        let prod = prods.find(p => (p.codigo_barra||'') === code);
        
        // ⚡ FIX: Si no encuentra el producto localmente, buscar en servidor
        if (!prod) {
          console.log('🔍 Producto no encontrado localmente, buscando en servidor...');
          try {
            const searchRes = await fetch(`/pos/search?q=${encodeURIComponent(code)}&limit=5`);
            if (searchRes.ok) {
              const searchResults = await searchRes.json();
              prod = searchResults.find(p => (p.codigo_barra||'') === code);
              
              if (prod) {
                // Agregar a allProducts para futuras búsquedas
                const existingIndex = prods.findIndex(existing => existing.id === prod.id);
                if (existingIndex >= 0) {
                  prods[existingIndex] = prod;
                } else {
                  prods.push(prod);
                }
                try { 
                  window.allProducts = prods; 
                  // ⚡ FIX: Sincronizar stock del producto encontrado
                  if (typeof window.syncStockForProducts === 'function') {
                    window.syncStockForProducts([prod]);
                  }
                } catch {}
                console.log(`➕ Producto ${prod.id} encontrado en servidor y agregado a cache`);
              }
            }
          } catch (serverError) {
            console.warn('Error buscando en servidor:', serverError);
          }
        }
        
        if (prod) {
          // ⚡ FIX: Verificar stock antes de agregar
          let hasStock = true;
          if (typeof window.stockDisponible !== 'undefined') {
            try {
              // Acceso indirecto al stock a través de DOM
              const productBtn = document.querySelector(`.product-btn[data-id="${prod.id}"]`);
              if (productBtn) {
                hasStock = !productBtn.disabled && parseInt(productBtn.dataset.stock || '0') > 0;
              }
            } catch {}
          }
          
          if (hasStock) {
            if (typeof window.addToCart === 'function') {
              window.addToCart(prod.id, prod.nombre, prod.precio);
            } else {
              // Fallback: buscar botón del producto y hacer click
              const btn = document.querySelector(`.product-btn[data-id="${prod.id}"]`);
              if (btn && !btn.disabled) btn.click();
            }
            setStatus(`✅ Agregado: ${prod.nombre}`, true);
          } else {
            setStatus(`❌ Sin stock: ${prod.nombre}`, false);
          }
        } else {
          setStatus('❌ Código no encontrado', false);
        }
      } catch (error) {
        console.error('Error al procesar código escaneado:', error);
        setStatus('❌ Error al procesar código', false);
      }
    } else {
      setStatus('✅ Código capturado', true);
    }
  }

  function onKeydown(e){
    if (!enabledEl || !enabledEl.checked) return;
    // Si la tecla viene muy lenta o no es candidata, no mezclar con buffer
    const now = Date.now();
    const delta = now - lastTs;
    lastTs = now;

    // Atajo: F9 para enfocar el buscador
    if (e.key === 'F9') {
      searchInput && searchInput.focus();
      return;
    }

    if (e.key === 'Enter' || e.key === 'Tab') {
      const code = buffer.trim();
      buffer = '';
      if (code) handleScanned(code);
      return;
    }

    if (delta > MAX_DELAY) {
      // Resetea si pasó mucho tiempo
      buffer = '';
    }

    if (e.key.length === 1) {
      buffer += e.key;
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    readPrefs();
    enabledEl && enabledEl.addEventListener('change', () => { savePrefs(); setStatus(enabledEl.checked ? 'Escáner activo' : 'Escáner inactivo', enabledEl.checked); });
    autoAddEl && autoAddEl.addEventListener('change', savePrefs);
    window.addEventListener('keydown', onKeydown, true);
  });
})();
