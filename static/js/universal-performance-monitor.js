// Monitor de Performance Universal para todas las páginas
class UniversalPerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.enabled = localStorage.getItem('global_debug') === 'true';
    this.pageType = this.detectPageType();
    this.storageKey = 'universal_performance_metrics';
    this.maxStoredMetrics = 100; // Límite para no saturar localStorage
    
    if (this.enabled) {
      console.log(`🔍 Monitor universal activado para página: ${this.pageType}`);
      this.loadStoredMetrics(); // Cargar métricas guardadas
      this.cleanupExistingPanels();
      this.createDebugPanel();
      this.setupAutoMetrics();
      this.logMetric(`${this.pageType} - Página cargada`, performance.now(), 'success');
    }
  }

  // Cargar métricas guardadas desde localStorage
  loadStoredMetrics() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      if (stored) {
        const data = JSON.parse(stored);
        // Filtrar métricas de las últimas 24 horas para no acumular infinitamente
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
        this.metrics = data.filter(metric => metric.timestamp > oneDayAgo);
        console.log(`📚 Cargadas ${this.metrics.length} métricas guardadas`);
      }
    } catch (error) {
      console.warn('⚠️ Error cargando métricas guardadas:', error);
      this.metrics = [];
    }
  }

  // Guardar métricas en localStorage
  saveMetrics() {
    try {
      // Mantener solo las métricas más recientes para no saturar el storage
      const metricsToStore = this.metrics.slice(-this.maxStoredMetrics);
      localStorage.setItem(this.storageKey, JSON.stringify(metricsToStore));
    } catch (error) {
      console.warn('⚠️ Error guardando métricas:', error);
      // Si el localStorage está lleno, limpiar métricas antiguas
      this.clearOldMetrics();
    }
  }

  // Limpiar métricas antiguas si el storage está lleno
  clearOldMetrics() {
    try {
      const recentMetrics = this.metrics.slice(-50); // Solo las últimas 50
      localStorage.setItem(this.storageKey, JSON.stringify(recentMetrics));
      this.metrics = recentMetrics;
      console.log('🧹 Métricas antiguas limpiadas por falta de espacio');
    } catch (error) {
      // Si aún falla, limpiar todo
      localStorage.removeItem(this.storageKey);
      this.metrics = [];
      console.log('🗑️ Storage limpiado completamente');
    }
  }

  // Detectar tipo de página automáticamente
  detectPageType() {
    const path = window.location.pathname;
    if (path.includes('/pos')) return 'POS';
    if (path.includes('/productos')) return 'Productos';
    if (path.includes('/transacciones')) return 'Transacciones';
    if (path.includes('/cierre')) return 'Cierres';
    if (path.includes('/reporte')) return 'Reportes';
    if (path.includes('/login')) return 'Login';
    if (path === '/' || path === '/home') return 'Home';
    return 'General';
  }

  // Limpiar paneles duplicados
  cleanupExistingPanels() {
    const existingPanels = document.querySelectorAll('[id*="performance-debug-panel"]');
    existingPanels.forEach(panel => panel.remove());
    if (existingPanels.length > 0) {
      console.log(`🧹 Limpiados ${existingPanels.length} paneles duplicados`);
    }
  }

  // Configurar métricas automáticas según el tipo de página
  setupAutoMetrics() {
    // Medir tiempo de carga de la página
    window.addEventListener('load', () => {
      const loadTime = performance.now();
      this.logMetric(`${this.pageType} - Carga página`, loadTime, 'success');
    });

    // Interceptar requests de fetch automáticamente
    this.interceptFetch();

    // Métricas específicas por página
    switch (this.pageType) {
      case 'POS':
        this.setupPOSMetrics();
        break;
      case 'Productos':
        this.setupProductsMetrics();
        break;
      case 'Transacciones':
        this.setupTransactionsMetrics();
        break;
    }
  }

  // Interceptar todas las llamadas fetch para medirlas automáticamente
  interceptFetch() {
    const originalFetch = window.fetch;
    window.fetch = async (...args) => {
      const start = performance.now();
      const url = args[0];
      
      try {
        const response = await originalFetch(...args);
        const duration = performance.now() - start;
        
        // Extraer endpoint limpio para la métrica
        const endpoint = this.extractEndpoint(url);
        this.logMetric(`API: ${endpoint}`, duration, response.ok ? 'success' : 'error');
        
        return response;
      } catch (error) {
        const duration = performance.now() - start;
        const endpoint = this.extractEndpoint(url);
        this.logMetric(`API: ${endpoint}`, duration, 'error');
        throw error;
      }
    };
  }

  // Extraer endpoint limpio de la URL
  extractEndpoint(url) {
    try {
      const urlObj = new URL(url, window.location.origin);
      let path = urlObj.pathname;
      
      // Simplificar rutas comunes
      if (path.includes('/pos/products')) return 'GET /pos/products';
      if (path.includes('/pos/search')) return 'GET /pos/search';
      if (path.includes('/web/productos')) return 'GET /productos';
      if (path.includes('/api/transacciones')) return 'GET /transacciones';
      
      return `${path}`;
    } catch {
      return String(url).substring(0, 30);
    }
  }

  // Métricas específicas para POS
  setupPOSMetrics() {
    console.log('📊 Configurando métricas específicas para POS');
    // Las métricas específicas del POS ya están en pos.js
  }

  // Métricas específicas para Productos
  setupProductsMetrics() {
    console.log('📊 Configurando métricas específicas para Productos');
    // Monitorear búsquedas de productos
    const searchInput = document.querySelector('input[type="search"], #search-input');
    if (searchInput) {
      let searchTimeout;
      searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
          const start = performance.now();
          // La métrica se registrará automáticamente por el interceptor de fetch
        }, 300);
      });
    }
  }

  // Métricas específicas para Transacciones
  setupTransactionsMetrics() {
    console.log('📊 Configurando métricas específicas para Transacciones');
  }

  // Medir función asíncrona
  async measureAsync(name, asyncFunction) {
    if (!this.enabled) return await asyncFunction();
    
    const start = performance.now();
    try {
      const result = await asyncFunction();
      const duration = performance.now() - start;
      this.logMetric(name, duration, 'success');
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      this.logMetric(name, duration, 'error');
      throw error;
    }
  }

  // Medir función síncrona
  measure(name, syncFunction) {
    if (!this.enabled) return syncFunction();
    
    const start = performance.now();
    try {
      const result = syncFunction();
      const duration = performance.now() - start;
      this.logMetric(name, duration, 'success');
      return result;
    } catch (error) {
      const duration = performance.now() - start;
      this.logMetric(name, duration, 'error');
      throw error;
    }
  }

  // Registrar métrica
  logMetric(name, duration, status = 'success') {
    const metric = {
      name,
      duration: Math.round(duration * 100) / 100,
      status,
      timestamp: new Date().toISOString(),
      page: this.pageType,
      session: this.getSessionId() // Para poder filtrar por sesión
    };
    
    this.metrics.push(metric);
    
    // Mantener solo las últimas métricas en memoria
    if (this.metrics.length > this.maxStoredMetrics) {
      this.metrics = this.metrics.slice(-this.maxStoredMetrics);
    }
    
    // Guardar en localStorage (pero no en cada métrica para evitar spam)
    this.debouncedSave();
    
    this.updateDebugPanel();
    
    // Log en consola para métricas importantes
    if (duration > 1000 || status === 'error') {
      const emoji = status === 'error' ? '❌' : '⚠️';
      console.log(`${emoji} ${name}: ${duration}ms`);
    }
  }

  // Obtener ID de sesión simple (para filtrar métricas por sesión)
  getSessionId() {
    if (!this.sessionId) {
      this.sessionId = Date.now().toString(36);
    }
    return this.sessionId;
  }

  // Guardar con debounce para no saturar localStorage
  debouncedSave() {
    clearTimeout(this.saveTimeout);
    this.saveTimeout = setTimeout(() => {
      this.saveMetrics();
    }, 1000); // Guardar cada segundo máximo
  }

  // Crear panel de debug
  createDebugPanel() {
    if (document.getElementById('universal-performance-panel')) {
      return;
    }
    
    const panel = document.createElement('div');
    panel.id = 'universal-performance-panel';
    panel.innerHTML = `
      <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.92);
        color: white;
        padding: 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 11px;
        z-index: 10001;
        max-width: 350px;
        max-height: 500px;
        overflow-y: auto;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        border: 1px solid #555;
        backdrop-filter: blur(4px);
      ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <div>
            <strong>🚀 Performance Monitor</strong>
            <div style="font-size: 9px; color: #888; margin-top: 2px;">${this.pageType}</div>
          </div>
          <button onclick="window.universalMonitor?.toggle?.()" style="
            background: #444; color: white; border: none; border-radius: 4px; 
            padding: 2px 6px; cursor: pointer; font-size: 10px;
          ">×</button>
        </div>
        <div id="universal-debug-metrics"></div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #444; display: flex; flex-wrap: wrap; gap: 3px;">
          <button onclick="window.universalMonitor?.clearCurrentSession?.()" style="
            background: #d97706; color: white; border: none; border-radius: 4px; 
            padding: 3px 6px; cursor: pointer; font-size: 9px; flex: 1;
          " title="Limpiar solo métricas de esta sesión">Esta sesión</button>
          <button onclick="window.universalMonitor?.clearAll?.()" style="
            background: #dc2626; color: white; border: none; border-radius: 4px; 
            padding: 3px 6px; cursor: pointer; font-size: 9px; flex: 1;
          " title="Limpiar todas las métricas guardadas">Todo</button>
          <button onclick="window.universalMonitor?.export?.()" style="
            background: #16a34a; color: white; border: none; border-radius: 4px; 
            padding: 3px 6px; cursor: pointer; font-size: 9px; flex: 1;
          " title="Exportar métricas a JSON">Exportar</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(panel);
    console.log('✅ Panel universal de debug creado');
  }

  // Actualizar panel de debug
  updateDebugPanel() {
    const container = document.getElementById('universal-debug-metrics');
    if (!container) return;

    // Mostrar últimas 8 métricas
    const recent = this.metrics.slice(-8).reverse();
    container.innerHTML = recent.map(metric => {
      const color = metric.duration > 1000 ? '#dc2626' : 
                   metric.duration > 500 ? '#d97706' : 
                   metric.duration > 200 ? '#f59e0b' : '#16a34a';
      const emoji = metric.status === 'success' ? '✅' : '❌';
      
      return `
        <div style="margin: 1px 0; color: ${color}; font-size: 10px;">
          ${emoji} ${metric.name}: <strong>${metric.duration}ms</strong>
        </div>
      `;
    }).join('');

    // Estadísticas generales
    if (this.metrics.length > 0) {
      const avgDuration = this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length;
      const maxDuration = Math.max(...this.metrics.map(m => m.duration));
      const errorCount = this.metrics.filter(m => m.status === 'error').length;
      
      // Contar métricas por sesión
      const currentSession = this.getSessionId();
      const currentSessionMetrics = this.metrics.filter(m => m.session === currentSession).length;
      const totalSessions = new Set(this.metrics.map(m => m.session)).size;
      
      container.innerHTML += `
        <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid #444; font-size: 9px; color: #ccc;">
          <div>📊 Promedio: ${Math.round(avgDuration)}ms</div>
          <div>⚡ Máximo: ${Math.round(maxDuration)}ms</div>
          <div>📈 Total: ${this.metrics.length} | 🔥 Actual: ${currentSessionMetrics}</div>
          <div>❌ Errores: ${errorCount} | 📅 Sesiones: ${totalSessions}</div>
        </div>
      `;
    }
  }

  // Mostrar/ocultar panel
  toggle() {
    const panel = document.getElementById('universal-performance-panel');
    if (panel) {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
  }

  // Limpiar métricas
  clear(onlySession = false) {
    if (onlySession) {
      // Solo limpiar métricas de la sesión actual
      const currentSession = this.getSessionId();
      const beforeCount = this.metrics.length;
      this.metrics = this.metrics.filter(m => m.session !== currentSession);
      const cleared = beforeCount - this.metrics.length;
      console.log(`🗑️ Limpiadas ${cleared} métricas de la sesión actual`);
    } else {
      // Limpiar todas las métricas
      this.metrics = [];
      localStorage.removeItem(this.storageKey);
      console.log('🗑️ Todas las métricas limpiadas');
    }
    
    this.updateDebugPanel();
  }

  // Limpiar solo métricas actuales (nuevo método para el botón)
  clearCurrentSession() {
    this.clear(true);
  }

  // Limpiar todo (método para el botón avanzado)
  clearAll() {
    this.clear(false);
  }

  // Exportar métricas
  export() {
    const data = {
      page: this.pageType,
      metrics: this.metrics,
      summary: this.getSummary(),
      timestamp: new Date().toISOString(),
      url: window.location.href
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-${this.pageType}-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('📤 Métricas exportadas');
  }

  // Obtener resumen de métricas
  getSummary() {
    if (this.metrics.length === 0) return null;
    
    const durations = this.metrics.map(m => m.duration);
    const errors = this.metrics.filter(m => m.status === 'error').length;
    
    return {
      totalOperations: this.metrics.length,
      averageDuration: durations.reduce((sum, d) => sum + d, 0) / durations.length,
      maxDuration: Math.max(...durations),
      minDuration: Math.min(...durations),
      errorRate: (errors / this.metrics.length) * 100,
      pageType: this.pageType
    };
  }

  // Simulación de latencia para testing
  async simulateNetworkDelay(ms = 200) {
    if (!this.enabled) return;
    await new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Auto-inicializar si está habilitado el debug global
document.addEventListener('DOMContentLoaded', () => {
  if (localStorage.getItem('global_debug') === 'true' && !window.universalMonitor) {
    window.universalMonitor = new UniversalPerformanceMonitor();
  }
});
