// Cache Inteligente para Productos - Mejora la velocidad sin tocar código base
class ProductCache {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    this.maxCacheSize = 1000; // Máximo 1000 productos en cache
    this.lastUpdateTime = new Map();
    
    console.log('🚀 Cache de productos inicializado');
  }

  // Generar clave de cache
  generateCacheKey(url, params = {}) {
    const urlObj = new URL(url, window.location.origin);
    
    // Normalizar parámetros de búsqueda
    const searchParams = new URLSearchParams(urlObj.search);
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined) {
        searchParams.set(key, params[key]);
      }
    });
    
    // Ordenar parámetros para consistencia
    searchParams.sort();
    
    return `${urlObj.pathname}?${searchParams.toString()}`;
  }

  // Verificar si el cache es válido
  isCacheValid(key) {
    const lastUpdate = this.lastUpdateTime.get(key);
    if (!lastUpdate) return false;
    
    const now = Date.now();
    return (now - lastUpdate) < this.cacheTimeout;
  }

  // Obtener del cache
  get(key) {
    if (!this.isCacheValid(key)) {
      this.cache.delete(key);
      this.lastUpdateTime.delete(key);
      return null;
    }
    
    const cached = this.cache.get(key);
    if (cached) {
      console.log(`📦 Cache hit: ${key}`);
      return JSON.parse(JSON.stringify(cached)); // Deep copy
    }
    
    return null;
  }

  // Guardar en cache
  set(key, data) {
    // Limpiar cache si está lleno
    if (this.cache.size >= this.maxCacheSize) {
      this.clearOldestEntries();
    }
    
    this.cache.set(key, JSON.parse(JSON.stringify(data))); // Deep copy
    this.lastUpdateTime.set(key, Date.now());
    
    console.log(`💾 Cached: ${key}`);
  }

  // Limpiar entradas más antiguas
  clearOldestEntries() {
    const entries = Array.from(this.lastUpdateTime.entries());
    entries.sort((a, b) => a[1] - b[1]); // Ordenar por tiempo
    
    // Eliminar el 25% más antiguo
    const toDelete = Math.floor(entries.length * 0.25);
    for (let i = 0; i < toDelete; i++) {
      const [key] = entries[i];
      this.cache.delete(key);
      this.lastUpdateTime.delete(key);
    }
    
    console.log(`🧹 Limpiadas ${toDelete} entradas antiguas del cache`);
  }

  // Invalidar cache de una URL específica
  invalidate(pattern) {
    let deletedCount = 0;
    
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
        this.lastUpdateTime.delete(key);
        deletedCount++;
      }
    }
    
    if (deletedCount > 0) {
      console.log(`🗑️ Invalidadas ${deletedCount} entradas del cache para: ${pattern}`);
    }
  }

  // Limpiar todo el cache
  clear() {
    const size = this.cache.size;
    this.cache.clear();
    this.lastUpdateTime.clear();
    console.log(`🔥 Cache completamente limpiado (${size} entradas)`);
  }

  // Obtener estadísticas del cache
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxCacheSize,
      timeoutMinutes: this.cacheTimeout / (60 * 1000),
      keys: Array.from(this.cache.keys())
    };
  }
}

// Instancia global del cache
window.productCache = new ProductCache();

// Interceptor de fetch para cache automático
const originalFetch = window.fetch;
window.fetch = async function(url, options = {}) {
  const method = options.method || 'GET';
  
  // Solo cachear requests GET de productos
  if (method === 'GET' && (url.includes('/productos') || url.includes('/pos/products'))) {
    const cacheKey = window.productCache.generateCacheKey(url);
    
    // Intentar obtener del cache primero
    const cached = window.productCache.get(cacheKey);
    if (cached) {
      // Simular respuesta de fetch con datos del cache
      return Promise.resolve(new Response(JSON.stringify(cached), {
        status: 200,
        statusText: 'OK',
        headers: {
          'Content-Type': 'application/json',
          'X-Cache': 'HIT'
        }
      }));
    }
  }
  
  // Si no hay cache, hacer request normal
  const startTime = performance.now();
  const response = await originalFetch(url, options);
  const duration = performance.now() - startTime;
  
  // Si es GET de productos y la respuesta es exitosa, cachear
  if (method === 'GET' && response.ok && (url.includes('/productos') || url.includes('/pos/products'))) {
    try {
      const clonedResponse = response.clone();
      const data = await clonedResponse.json();
      
      const cacheKey = window.productCache.generateCacheKey(url);
      window.productCache.set(cacheKey, data);
      
      // Agregar header para indicar que viene del servidor
      response.headers.set('X-Cache', 'MISS');
      response.headers.set('X-Response-Time', `${duration.toFixed(2)}ms`);
      
    } catch (error) {
      console.warn('Error cacheando respuesta:', error);
    }
  }
  
  return response;
};

// Funciones de utilidad para invalidar cache cuando sea necesario
window.invalidateProductCache = function(pattern = '/productos') {
  window.productCache.invalidate(pattern);
};

window.clearProductCache = function() {
  window.productCache.clear();
};

window.getProductCacheStats = function() {
  const stats = window.productCache.getStats();
  console.table(stats);
  return stats;
};

// Auto-limpiar cache cuando se detectan cambios (por ejemplo, después de crear/editar)
document.addEventListener('visibilitychange', function() {
  if (document.hidden) {
    // Cuando la página se oculta, limpiar cache de productos para asegurar datos frescos
    setTimeout(() => {
      window.productCache.invalidate('/productos');
    }, 1000);
  }
});

console.log('✅ Sistema de cache de productos instalado - Mejorará la velocidad de carga');
