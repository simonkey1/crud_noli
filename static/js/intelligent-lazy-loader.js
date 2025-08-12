// Lazy Loading Inteligente - Carga progresiva de contenido
class IntelligentLazyLoader {
  constructor() {
    this.observer = null;
    this.imageObserver = null;
    this.loadedElements = new Set();
    this.loadingElements = new Set();
    this.preloadDistance = 100; // Distancia en px para pre-cargar
    this.imageCache = new Map();
    
    this.init();
    console.log('🖼️ Lazy loading inteligente inicializado');
  }

  // Inicializar lazy loading
  init() {
    this.setupIntersectionObserver();
    this.setupImageObserver();
    this.processExistingContent();
    this.setupPreloading();
  }

  // Configurar Intersection Observer
  setupIntersectionObserver() {
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver no soportado, cargando todo inmediatamente');
      this.loadAllContent();
      return;
    }

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting || entry.intersectionRatio > 0) {
          this.loadElement(entry.target);
        }
      });
    }, {
      rootMargin: `${this.preloadDistance}px`,
      threshold: [0, 0.1, 0.5]
    });
  }

  // Configurar observer específico para imágenes
  setupImageObserver() {
    this.imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadImage(entry.target);
        }
      });
    }, {
      rootMargin: `${this.preloadDistance * 2}px`,
      threshold: 0.01
    });
  }

  // Procesar contenido existente
  processExistingContent() {
    // Observar imágenes
    this.observeImages();
    
    // Observar contenido lazy
    this.observeLazyContent();
    
    // Observar tablas grandes
    this.observeLargeTables();
  }

  // Observar imágenes para lazy loading
  observeImages() {
    const images = document.querySelectorAll('img[data-src], img[src]');
    
    images.forEach(img => {
      if (img.dataset.lazyProcessed) return;
      
      img.dataset.lazyProcessed = 'true';
      
      // Si tiene data-src, es para lazy loading
      if (img.dataset.src) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        this.imageObserver.observe(img);
      } else {
        // Optimizar imágenes existentes
        this.optimizeExistingImage(img);
      }
    });
  }

  // Observar contenido lazy
  observeLazyContent() {
    const lazyElements = document.querySelectorAll('[data-lazy], .lazy-load');
    
    lazyElements.forEach(element => {
      if (!this.loadedElements.has(element)) {
        this.observer.observe(element);
      }
    });
  }

  // Observar tablas grandes
  observeLargeTables() {
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
      const rows = table.querySelectorAll('tbody tr');
      if (rows.length > 20) {
        this.virtualizeTable(table);
      }
    });
  }

  // Cargar imagen
  async loadImage(img) {
    if (this.loadingElements.has(img) || this.loadedElements.has(img)) {
      return;
    }

    this.loadingElements.add(img);
    this.imageObserver.unobserve(img);

    try {
      const src = img.dataset.src || img.src;
      
      // Verificar caché
      if (this.imageCache.has(src)) {
        const cachedBlob = this.imageCache.get(src);
        img.src = URL.createObjectURL(cachedBlob);
        this.onImageLoaded(img);
        return;
      }

      // Mostrar placeholder mientras carga
      this.showImagePlaceholder(img);

      // Cargar imagen
      const response = await fetch(src);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const blob = await response.blob();
      
      // Guardar en caché
      this.imageCache.set(src, blob);
      
      // Crear URL y mostrar
      const imageUrl = URL.createObjectURL(blob);
      img.src = imageUrl;
      
      this.onImageLoaded(img);
      
    } catch (error) {
      console.warn('Error cargando imagen:', error);
      this.onImageError(img);
    } finally {
      this.loadingElements.delete(img);
      this.loadedElements.add(img);
    }
  }

  // Mostrar placeholder de imagen
  showImagePlaceholder(img) {
    if (img.dataset.placeholder !== 'false') {
      const placeholder = this.createImagePlaceholder(img);
      img.style.background = `url(${placeholder}) center/cover`;
    }
  }

  // Crear placeholder de imagen
  createImagePlaceholder(img) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 400;
    canvas.height = 300;
    
    // Gradiente de placeholder
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, '#f0f0f0');
    gradient.addColorStop(1, '#e0e0e0');
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Ícono de imagen
    ctx.fillStyle = '#ccc';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('🖼️', canvas.width / 2, canvas.height / 2 + 16);
    
    return canvas.toDataURL();
  }

  // Imagen cargada exitosamente
  onImageLoaded(img) {
    img.style.opacity = '1';
    img.style.background = 'none';
    
    // Disparar evento personalizado
    img.dispatchEvent(new CustomEvent('lazyLoaded', {
      detail: { src: img.src }
    }));
  }

  // Error al cargar imagen
  onImageError(img) {
    img.style.opacity = '0.5';
    img.alt = 'Error al cargar imagen';
    
    // Mostrar placeholder de error
    const errorPlaceholder = this.createErrorPlaceholder();
    img.style.background = `url(${errorPlaceholder}) center/cover`;
  }

  // Crear placeholder de error
  createErrorPlaceholder() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    canvas.width = 400;
    canvas.height = 300;
    
    ctx.fillStyle = '#ffebee';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#f44336';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('⚠️', canvas.width / 2, canvas.height / 2 + 16);
    
    return canvas.toDataURL();
  }

  // Optimizar imagen existente
  optimizeExistingImage(img) {
    // Verificar si la imagen es muy grande
    if (img.naturalWidth > 800 || img.naturalHeight > 600) {
      img.style.imageRendering = 'auto';
      img.style.imageRendering = '-webkit-optimize-contrast';
    }
    
    // Agregar loading="lazy" si el navegador lo soporta
    if ('loading' in HTMLImageElement.prototype) {
      img.loading = 'lazy';
    }
  }

  // Cargar elemento
  loadElement(element) {
    if (this.loadedElements.has(element) || this.loadingElements.has(element)) {
      return;
    }

    this.loadingElements.add(element);
    this.observer.unobserve(element);

    try {
      // Diferentes tipos de carga lazy
      if (element.dataset.lazy === 'table') {
        this.loadTableContent(element);
      } else if (element.dataset.lazy === 'component') {
        this.loadComponent(element);
      } else if (element.classList.contains('lazy-load')) {
        this.loadGenericContent(element);
      }

    } catch (error) {
      console.warn('Error cargando elemento lazy:', error);
    } finally {
      this.loadingElements.delete(element);
      this.loadedElements.add(element);
    }
  }

  // Cargar contenido de tabla
  loadTableContent(table) {
    const hiddenRows = table.querySelectorAll('tr[data-lazy-row]');
    
    hiddenRows.forEach((row, index) => {
      setTimeout(() => {
        row.style.display = '';
        row.style.opacity = '0';
        row.style.transform = 'translateY(20px)';
        row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        
        requestAnimationFrame(() => {
          row.style.opacity = '1';
          row.style.transform = 'translateY(0)';
        });
      }, index * 50); // Staggered loading
    });
  }

  // Cargar componente
  async loadComponent(element) {
    const componentUrl = element.dataset.componentUrl;
    if (!componentUrl) return;

    try {
      const response = await fetch(componentUrl);
      const html = await response.text();
      
      element.innerHTML = html;
      
      // Procesar nuevo contenido
      this.processExistingContent();
      
    } catch (error) {
      element.innerHTML = '<div class="text-red-500">Error cargando componente</div>';
    }
  }

  // Cargar contenido genérico
  loadGenericContent(element) {
    element.classList.remove('lazy-load');
    element.classList.add('lazy-loaded');
    
    // Animación de entrada
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    
    requestAnimationFrame(() => {
      element.style.opacity = '1';
      element.style.transform = 'translateY(0)';
    });
  }

  // Virtualizar tabla grande
  virtualizeTable(table) {
    const tbody = table.querySelector('tbody');
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll('tr'));
    const visibleRows = 20;
    const bufferRows = 5;

    // Ocultar filas no visibles
    rows.forEach((row, index) => {
      if (index >= visibleRows) {
        row.style.display = 'none';
        row.dataset.lazyRow = 'true';
      }
    });

    // Agregar botón "Cargar más"
    this.addLoadMoreButton(table, rows, visibleRows);
  }

  // Agregar botón "Cargar más"
  addLoadMoreButton(table, allRows, currentVisible) {
    const loadMoreBtn = document.createElement('button');
    loadMoreBtn.textContent = `Cargar más (${allRows.length - currentVisible} restantes)`;
    loadMoreBtn.className = 'btn btn-secondary mt-3 w-full';
    
    let visibleCount = currentVisible;
    
    loadMoreBtn.addEventListener('click', () => {
      const nextBatch = Math.min(20, allRows.length - visibleCount);
      
      for (let i = visibleCount; i < visibleCount + nextBatch; i++) {
        if (allRows[i]) {
          allRows[i].style.display = '';
          
          // Animación de entrada
          setTimeout(() => {
            allRows[i].style.opacity = '0';
            allRows[i].style.transform = 'translateY(10px)';
            allRows[i].style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            
            requestAnimationFrame(() => {
              allRows[i].style.opacity = '1';
              allRows[i].style.transform = 'translateY(0)';
            });
          }, (i - visibleCount) * 50);
        }
      }
      
      visibleCount += nextBatch;
      
      if (visibleCount >= allRows.length) {
        loadMoreBtn.remove();
      } else {
        loadMoreBtn.textContent = `Cargar más (${allRows.length - visibleCount} restantes)`;
      }
    });

    table.parentElement.appendChild(loadMoreBtn);
  }

  // Configurar preloading inteligente
  setupPreloading() {
    // Precargar imágenes en enlaces hover
    document.addEventListener('mouseenter', (event) => {
      const link = event.target.closest('a[href]');
      if (link && link.href.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
        this.preloadImage(link.href);
      }
    }, true);

    // Precargar contenido relacionado
    this.preloadRelatedContent();
  }

  // Precargar imagen
  preloadImage(src) {
    if (this.imageCache.has(src)) return;

    const img = new Image();
    img.onload = () => {
      // Convertir a blob para caché
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);
      
      canvas.toBlob(blob => {
        if (blob) this.imageCache.set(src, blob);
      });
    };
    img.src = src;
  }

  // Precargar contenido relacionado
  preloadRelatedContent() {
    // Precargar próximas páginas de productos
    const nextPageLinks = document.querySelectorAll('a[href*="page="], .pagination a');
    nextPageLinks.forEach(link => {
      if (link.href && !link.href.includes(window.location.href)) {
        this.preloadPageContent(link.href);
      }
    });
  }

  // Precargar contenido de página
  async preloadPageContent(url) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      if (response.ok) {
        console.log(`📄 Página precargada: ${url}`);
      }
    } catch (error) {
      // Silenciar errores de precarga
    }
  }

  // Cargar todo el contenido (fallback)
  loadAllContent() {
    const lazyElements = document.querySelectorAll('[data-lazy], .lazy-load, img[data-src]');
    lazyElements.forEach(element => {
      if (element.tagName === 'IMG' && element.dataset.src) {
        element.src = element.dataset.src;
        this.onImageLoaded(element);
      } else {
        this.loadElement(element);
      }
    });
  }

  // Obtener estadísticas
  getStats() {
    return {
      loadedElements: this.loadedElements.size,
      loadingElements: this.loadingElements.size,
      cachedImages: this.imageCache.size,
      cacheSize: this.calculateCacheSize(),
      supportIntersectionObserver: 'IntersectionObserver' in window
    };
  }

  // Calcular tamaño de caché
  calculateCacheSize() {
    let totalSize = 0;
    for (const blob of this.imageCache.values()) {
      totalSize += blob.size;
    }
    return `${(totalSize / 1024 / 1024).toFixed(2)} MB`;
  }

  // Limpiar caché
  clearCache() {
    this.imageCache.clear();
    console.log('🧹 Caché de imágenes limpiado');
  }
}

// Instancia global
window.intelligentLazyLoader = new IntelligentLazyLoader();

// Funciones de utilidad globales
window.getLazyLoadStats = function() {
  return window.intelligentLazyLoader?.getStats();
};

window.clearImageCache = function() {
  window.intelligentLazyLoader?.clearCache();
};

// Re-inicializar cuando se añade contenido dinámico
window.reinitializeLazyLoading = function() {
  window.intelligentLazyLoader?.processExistingContent();
};

console.log('✅ Lazy loading inteligente instalado - Carga progresiva optimizada');
