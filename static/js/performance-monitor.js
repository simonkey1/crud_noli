// Utilidad para medir rendimiento en el POS
class PerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.enabled = localStorage.getItem('pos_debug') === 'true';
    
    if (this.enabled) {
      console.log('🔍 Monitor de rendimiento activado');
      this.cleanupExistingPanels(); // Limpiar paneles duplicados
      this.createDebugPanel();
    }
  }

  // Limpiar paneles duplicados
  cleanupExistingPanels() {
    const existingPanels = document.querySelectorAll('#performance-debug-panel');
    existingPanels.forEach(panel => panel.remove());
    console.log(`🧹 Limpiados ${existingPanels.length} paneles duplicados`);
  }

  // Medir tiempo de una operación
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

  // Simular latencia de red para testing local
  async simulateNetworkDelay(ms = 200) {
    if (!this.enabled) return;
    await new Promise(resolve => setTimeout(resolve, ms));
  }

  logMetric(name, duration, status) {
    const metric = {
      name,
      duration: Math.round(duration * 100) / 100,
      status,
      timestamp: new Date().toISOString()
    };
    
    this.metrics.push(metric);
    
    // Mantener solo últimas 100 métricas
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }

    // Log con colores
    const emoji = status === 'success' ? '✅' : '❌';
    const color = duration > 1000 ? 'red' : duration > 500 ? 'orange' : 'green';
    
    console.log(
      `%c${emoji} ${name}: ${duration}ms`,
      `color: ${color}; font-weight: bold`
    );

    this.updateDebugPanel();
  }

  createDebugPanel() {
    // Verificar si ya existe un panel para evitar duplicados
    if (document.getElementById('performance-debug-panel')) {
      console.log('⚠️ Panel de debug ya existe, no creando duplicado');
      return;
    }
    
    // Crear panel flotante de debug
    const panel = document.createElement('div');
    panel.id = 'performance-debug-panel';
    panel.innerHTML = `
      <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.9);
        color: white;
        padding: 12px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
        z-index: 10000;
        max-width: 320px;
        max-height: 450px;
        overflow-y: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 1px solid #444;
      ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <strong>📊 Performance Monitor</strong>
          <button onclick="window.performanceMonitor?.toggle?.()" style="background: #444; color: white; border: none; border-radius: 4px; padding: 2px 6px; cursor: pointer; font-size: 10px;">
            ×
          </button>
        </div>
        <div id="debug-metrics"></div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #444;">
          <button onclick="window.performanceMonitor?.clear?.()" style="background: #dc2626; color: white; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer; margin-right: 5px; font-size: 10px;">
            Limpiar
          </button>
          <button onclick="window.performanceMonitor?.export?.()" style="background: #16a34a; color: white; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer; font-size: 10px;">
            Exportar
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(panel);
    console.log('✅ Panel de debug creado');
  }

  updateDebugPanel() {
    const container = document.getElementById('debug-metrics');
    if (!container) return;

    // Mostrar últimas 10 métricas
    const recent = this.metrics.slice(-10).reverse();
    container.innerHTML = recent.map(metric => {
      const color = metric.duration > 1000 ? '#dc2626' : 
                   metric.duration > 500 ? '#d97706' : '#16a34a';
      const emoji = metric.status === 'success' ? '✅' : '❌';
      
      return `
        <div style="margin: 2px 0; color: ${color};">
          ${emoji} ${metric.name}: <strong>${metric.duration}ms</strong>
        </div>
      `;
    }).join('');

    // Estadísticas
    if (this.metrics.length > 0) {
      const avgDuration = this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length;
      const maxDuration = Math.max(...this.metrics.map(m => m.duration));
      
      container.innerHTML += `
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #444; font-size: 11px;">
          <div>Promedio: ${Math.round(avgDuration)}ms</div>
          <div>Máximo: ${Math.round(maxDuration)}ms</div>
          <div>Total: ${this.metrics.length} ops</div>
        </div>
      `;
    }
  }

  toggle() {
    const panel = document.getElementById('performance-debug-panel');
    if (panel) {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    }
  }

  clear() {
    this.metrics = [];
    this.updateDebugPanel();
    console.log('🗑️ Métricas de rendimiento limpiadas');
  }

  export() {
    const data = {
      metrics: this.metrics,
      summary: this.getSummary(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pos-performance-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log('📊 Métricas exportadas', data);
  }

  getSummary() {
    if (this.metrics.length === 0) return {};

    const durations = this.metrics.map(m => m.duration);
    const successful = this.metrics.filter(m => m.status === 'success').length;
    
    return {
      total_operations: this.metrics.length,
      successful_operations: successful,
      error_rate: ((this.metrics.length - successful) / this.metrics.length * 100).toFixed(2) + '%',
      avg_duration: Math.round(durations.reduce((a, b) => a + b, 0) / durations.length),
      min_duration: Math.min(...durations),
      max_duration: Math.max(...durations),
      p95_duration: this.percentile(durations, 0.95),
      slow_operations: this.metrics.filter(m => m.duration > 1000).length
    };
  }

  percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = Math.ceil(sorted.length * p) - 1;
    return sorted[index];
  }

  // Activar/desactivar desde consola
  enable() {
    localStorage.setItem('pos_debug', 'true');
    location.reload();
  }

  disable() {
    localStorage.setItem('pos_debug', 'false');
    location.reload();
  }
}

// Crear instancia global
window.posPerformance = new PerformanceMonitor();

// Función helper para usar en el código
window.measurePerf = (name, fn) => posPerformance.measureAsync(name, fn);

// Comandos de consola para activar/desactivar
console.log(`
🔍 Monitor de rendimiento POS
Para activar: posPerformance.enable()
Para desactivar: posPerformance.disable()
Estado actual: ${localStorage.getItem('pos_debug') === 'true' ? 'ACTIVADO' : 'DESACTIVADO'}
`);
