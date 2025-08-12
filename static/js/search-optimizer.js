// Optimizador de Búsqueda - Debounce y cache inteligente
class SearchOptimizer {
  constructor() {
    this.searchCache = new Map();
    this.searchTimeouts = new Map();
    this.searchHistory = new Map();
    this.debounceTime = 300;
    this.maxCacheSize = 100;
    this.maxHistorySize = 50;
    
    this.setupGlobalSearch();
    console.log('🔍 Optimizador de búsqueda inicializado');
  }

  // Configurar búsqueda global optimizada
  setupGlobalSearch() {
    // Interceptar y optimizar inputs de búsqueda
    this.observeSearchInputs();
    
    // Configurar shortcuts de teclado
    this.setupKeyboardShortcuts();
  }

  // Observar inputs de búsqueda para aplicar optimizaciones
  observeSearchInputs() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            this.enhanceSearchInputs(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Mejorar inputs existentes
    this.enhanceSearchInputs(document);
  }

  // Mejorar inputs de búsqueda
  enhanceSearchInputs(container) {
    const searchInputs = container.querySelectorAll(
      'input[type="search"], input[placeholder*="buscar"], input[placeholder*="Buscar"], input[id*="search"], input[class*="search"]'
    );

    searchInputs.forEach(input => {
      if (input.dataset.optimized) return;
      
      input.dataset.optimized = 'true';
      this.setupOptimizedInput(input);
    });
  }

  // Configurar input optimizado
  setupOptimizedInput(input) {
    let originalHandler = null;
    let searchFunction = null;

    // Detectar función de búsqueda existente
    const events = ['input', 'keyup', 'change'];
    events.forEach(event => {
      const listeners = input.cloneNode(true);
      // No podemos acceder directamente a listeners, así que usamos un approach diferente
    });

    // Crear nuevo handler optimizado
    const optimizedHandler = this.createOptimizedHandler(input);
    
    // Reemplazar eventos existentes
    events.forEach(event => {
      input.addEventListener(event, optimizedHandler);
    });

    // Agregar indicadores visuales
    this.addSearchIndicators(input);
    
    // Configurar autocompletado si es necesario
    this.setupAutoComplete(input);
  }

  // Crear handler optimizado con debounce
  createOptimizedHandler(input) {
    return (event) => {
      const query = input.value.trim();
      const inputId = input.id || input.name || 'search';
      
      // Limpiar timeout anterior
      if (this.searchTimeouts.has(inputId)) {
        clearTimeout(this.searchTimeouts.get(inputId));
      }

      // Mostrar indicador de búsqueda
      this.showSearchIndicator(input, true);

      // Configurar nuevo timeout
      const timeout = setTimeout(() => {
        this.performOptimizedSearch(input, query, inputId);
      }, this.debounceTime);

      this.searchTimeouts.set(inputId, timeout);

      // Si la búsqueda está vacía, ejecutar inmediatamente
      if (query === '') {
        clearTimeout(timeout);
        this.performOptimizedSearch(input, query, inputId);
      }
    };
  }

  // Realizar búsqueda optimizada
  async performOptimizedSearch(input, query, inputId) {
    try {
      // Ocultar indicador de búsqueda
      this.showSearchIndicator(input, false);

      // Verificar caché
      const cacheKey = `${inputId}:${query}`;
      if (this.searchCache.has(cacheKey)) {
        const cached = this.searchCache.get(cacheKey);
        this.applySearchResults(input, cached.results, query);
        
        // Actualizar estadísticas de uso
        cached.lastUsed = Date.now();
        cached.useCount++;
        
        console.log(`🎯 Búsqueda desde caché: "${query}"`);
        return;
      }

      // Buscar función de búsqueda original
      const searchFunction = this.findSearchFunction(input);
      
      if (searchFunction) {
        console.log(`🔍 Búsqueda optimizada: "${query}"`);
        
        // Ejecutar búsqueda original
        const startTime = performance.now();
        await searchFunction(query);
        const duration = performance.now() - startTime;

        // Guardar en caché si la búsqueda fue exitosa
        this.cacheSearchResult(cacheKey, null, query, duration);
        
        // Registrar en historial
        this.addToHistory(query, duration);
        
        // Reportar rendimiento si está disponible el monitor
        if (window.universalMonitor) {
          window.universalMonitor.recordOperation('search', duration, {
            query: query,
            inputId: inputId,
            cached: false
          });
        }
      }

    } catch (error) {
      console.error('Error en búsqueda optimizada:', error);
      this.showSearchIndicator(input, false);
    }
  }

  // Encontrar función de búsqueda original
  findSearchFunction(input) {
    // Buscar en el contexto global funciones de búsqueda comunes
    const possibleFunctions = [
      'filtrarProductos',
      'buscarProductos', 
      'filterProducts',
      'searchProducts',
      'search',
      'filter'
    ];

    for (const funcName of possibleFunctions) {
      if (typeof window[funcName] === 'function') {
        return window[funcName];
      }
    }

    // Buscar en formularios padre
    const form = input.closest('form');
    if (form && form.onsubmit) {
      return (query) => {
        input.value = query;
        form.onsubmit(new Event('submit'));
      };
    }

    return null;
  }

  // Aplicar resultados de búsqueda
  applySearchResults(input, results, query) {
    // Esta función sería específica según el tipo de búsqueda
    // Por ahora, solo disparamos eventos para que el código existente responda
    const event = new CustomEvent('optimizedSearch', {
      detail: { query, results, cached: true }
    });
    input.dispatchEvent(event);
  }

  // Guardar resultado en caché
  cacheSearchResult(key, results, query, duration) {
    // Limpiar caché si está lleno
    if (this.searchCache.size >= this.maxCacheSize) {
      const oldestKey = [...this.searchCache.entries()]
        .sort(([,a], [,b]) => a.lastUsed - b.lastUsed)[0][0];
      this.searchCache.delete(oldestKey);
    }

    this.searchCache.set(key, {
      results,
      query,
      duration,
      timestamp: Date.now(),
      lastUsed: Date.now(),
      useCount: 1
    });
  }

  // Agregar al historial
  addToHistory(query, duration) {
    if (query.length < 2) return;

    // Limpiar historial si está lleno
    if (this.searchHistory.size >= this.maxHistorySize) {
      const oldestKey = [...this.searchHistory.keys()][0];
      this.searchHistory.delete(oldestKey);
    }

    this.searchHistory.set(query, {
      lastUsed: Date.now(),
      duration,
      useCount: (this.searchHistory.get(query)?.useCount || 0) + 1
    });
  }

  // Mostrar indicador de búsqueda
  showSearchIndicator(input, show) {
    let indicator = input.parentElement.querySelector('.search-indicator');
    
    if (show && !indicator) {
      indicator = document.createElement('div');
      indicator.className = 'search-indicator';
      indicator.style.cssText = `
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        width: 16px;
        height: 16px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        pointer-events: none;
        z-index: 10;
      `;
      
      // Asegurar posición relativa del contenedor
      const container = input.parentElement;
      if (getComputedStyle(container).position === 'static') {
        container.style.position = 'relative';
      }
      
      container.appendChild(indicator);
      
    } else if (!show && indicator) {
      indicator.remove();
    }
  }

  // Agregar indicadores visuales
  addSearchIndicators(input) {
    // Agregar ícono de búsqueda si no existe
    if (!input.parentElement.querySelector('.search-icon')) {
      const icon = document.createElement('div');
      icon.className = 'search-icon';
      icon.innerHTML = '🔍';
      icon.style.cssText = `
        position: absolute;
        left: 8px;
        top: 50%;
        transform: translateY(-50%);
        pointer-events: none;
        opacity: 0.5;
        z-index: 10;
      `;
      
      const container = input.parentElement;
      if (getComputedStyle(container).position === 'static') {
        container.style.position = 'relative';
      }
      
      container.appendChild(icon);
      
      // Ajustar padding del input
      input.style.paddingLeft = '32px';
    }
  }

  // Configurar autocompletado
  setupAutoComplete(input) {
    const dropdown = document.createElement('div');
    dropdown.className = 'search-autocomplete';
    dropdown.style.cssText = `
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: white;
      border: 1px solid #ddd;
      border-top: none;
      max-height: 200px;
      overflow-y: auto;
      z-index: 1000;
      display: none;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    `;

    const container = input.parentElement;
    if (getComputedStyle(container).position === 'static') {
      container.style.position = 'relative';
    }
    
    container.appendChild(dropdown);

    // Manejar sugerencias
    input.addEventListener('focus', () => {
      this.showSuggestions(input, dropdown);
    });

    input.addEventListener('blur', () => {
      setTimeout(() => dropdown.style.display = 'none', 150);
    });
  }

  // Mostrar sugerencias
  showSuggestions(input, dropdown) {
    const suggestions = [...this.searchHistory.entries()]
      .sort(([,a], [,b]) => b.lastUsed - a.lastUsed)
      .slice(0, 5)
      .map(([query]) => query);

    if (suggestions.length === 0) {
      dropdown.style.display = 'none';
      return;
    }

    dropdown.innerHTML = suggestions.map(suggestion => `
      <div class="suggestion-item" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #eee;">
        <span style="opacity: 0.6;">🕐</span> ${suggestion}
      </div>
    `).join('');

    // Manejar clicks en sugerencias
    dropdown.querySelectorAll('.suggestion-item').forEach((item, index) => {
      item.addEventListener('click', () => {
        input.value = suggestions[index];
        input.dispatchEvent(new Event('input'));
        dropdown.style.display = 'none';
      });
    });

    dropdown.style.display = 'block';
  }

  // Configurar shortcuts de teclado
  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
      // Ctrl/Cmd + K para enfocar búsqueda
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[placeholder*="buscar"]');
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
      }
    });
  }

  // Obtener estadísticas de búsqueda
  getSearchStats() {
    return {
      cacheSize: this.searchCache.size,
      historySize: this.searchHistory.size,
      cacheHitRate: this.calculateCacheHitRate(),
      averageSearchTime: this.calculateAverageSearchTime(),
      topSearches: this.getTopSearches()
    };
  }

  // Calcular tasa de aciertos de caché
  calculateCacheHitRate() {
    const total = [...this.searchCache.values()].reduce((sum, item) => sum + item.useCount, 0);
    const hits = [...this.searchCache.values()].reduce((sum, item) => sum + (item.useCount - 1), 0);
    return total > 0 ? (hits / total * 100).toFixed(1) : 0;
  }

  // Calcular tiempo promedio de búsqueda
  calculateAverageSearchTime() {
    const durations = [...this.searchHistory.values()].map(item => item.duration);
    return durations.length > 0 ? 
      (durations.reduce((sum, d) => sum + d, 0) / durations.length).toFixed(1) : 0;
  }

  // Obtener búsquedas más populares
  getTopSearches() {
    return [...this.searchHistory.entries()]
      .sort(([,a], [,b]) => b.useCount - a.useCount)
      .slice(0, 5)
      .map(([query, data]) => ({ query, count: data.useCount }));
  }

  // Limpiar caché
  clearCache() {
    this.searchCache.clear();
    console.log('🧹 Caché de búsqueda limpiado');
  }

  // Limpiar historial
  clearHistory() {
    this.searchHistory.clear();
    console.log('🧹 Historial de búsqueda limpiado');
  }
}

// Instancia global
window.searchOptimizer = new SearchOptimizer();

// Funciones de utilidad globales
window.getSearchStats = function() {
  return window.searchOptimizer?.getSearchStats();
};

window.clearSearchCache = function() {
  window.searchOptimizer?.clearCache();
};

console.log('✅ Optimizador de búsqueda instalado - Búsquedas más rápidas con debounce y caché');
