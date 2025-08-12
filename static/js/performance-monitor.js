// Utilidad para medir rendimiento en el POS
class PerformanceMonitor {
  constructor() {
    this.metrics = [];
    this.enabled = localStorage.getItem('pos_debug') === 'true';
    
    if (this.enabled) {
      console.log('🔍 Monitor de rendimiento activado');
      this.createDebugPanel();
    }
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
    // Crear panel flotante de debug
    const panel = document.createElement('div');
    panel.id = 'performance-debug-panel';
    panel.innerHTML = `
      <div style="
        position: fixed;
        top: 10px;
        right: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
        z-index: 9999;
        max-width: 300px;
        max-height: 400px;
        overflow-y: auto;
      ">
        <div style="display: flex; justify-content: between; margin-bottom: 8px;">
          <strong>📊 Performance Monitor</strong>
          <button onclick="posPerformance.toggle()" style="margin-left: 10px; background: #333; color: white; border: none; border-radius: 4px; padding: 2px 6px; cursor: pointer;">
            Ocultar
          </button>
        </div>
        <div id="debug-metrics"></div>
        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #444;">
          <button onclick="posPerformance.clear()" style="background: #dc2626; color: white; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer; margin-right: 5px;">
            Limpiar
          </button>
          <button onclick="posPerformance.export()" style="background: #16a34a; color: white; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer;">
            Exportar
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(panel);
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
