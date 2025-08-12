// Preloader Inteligente - Mejora la percepción de velocidad
class IntelligentPreloader {
  constructor() {
    this.isActive = false;
    this.loadingElements = new Set();
    this.setupStyles();
    this.setupGlobalLoading();
    
    console.log('⚡ Preloader inteligente inicializado');
  }

  // Configurar estilos CSS
  setupStyles() {
    if (document.getElementById('intelligent-preloader-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'intelligent-preloader-styles';
    style.textContent = `
      /* Skeleton Loading */
      .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s infinite;
      }
      
      .dark .skeleton {
        background: linear-gradient(90deg, #374151 25%, #4b5563 50%, #374151 75%);
        background-size: 200% 100%;
      }
      
      @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
      
      /* Pulse loading */
      .pulse-loading {
        animation: pulse 1.5s ease-in-out infinite;
      }
      
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
      
      /* Loading overlay */
      .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        backdrop-filter: blur(2px);
      }
      
      .dark .loading-overlay {
        background: rgba(17, 24, 39, 0.8);
      }
      
      /* Spinner */
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      .dark .spinner {
        border: 4px solid #374151;
        border-top: 4px solid #60a5fa;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      /* Progress bar */
      .progress-bar {
        width: 100%;
        height: 4px;
        background-color: #f3f3f3;
        border-radius: 2px;
        overflow: hidden;
        position: relative;
      }
      
      .dark .progress-bar {
        background-color: #374151;
      }
      
      .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 2px;
        transition: width 0.3s ease;
      }
      
      .progress-bar-indeterminate {
        width: 30%;
        animation: progress-indeterminate 1.5s ease-in-out infinite;
      }
      
      @keyframes progress-indeterminate {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(400%); }
      }
    `;
    
    document.head.appendChild(style);
  }

  // Configurar indicadores de carga global
  setupGlobalLoading() {
    // Interceptar fetch para mostrar indicadores automáticamente
    const originalFetch = window.fetch;
    let activeRequests = 0;
    
    window.fetch = async function(...args) {
      const isProductRequest = args[0].includes('/productos') || args[0].includes('/pos/products');
      
      if (isProductRequest) {
        activeRequests++;
        window.intelligentPreloader?.showGlobalLoading();
      }
      
      try {
        const response = await originalFetch.apply(this, args);
        return response;
      } finally {
        if (isProductRequest) {
          activeRequests--;
          if (activeRequests === 0) {
            window.intelligentPreloader?.hideGlobalLoading();
          }
        }
      }
    };
  }

  // Mostrar carga global (barra de progreso en la parte superior)
  showGlobalLoading() {
    if (document.getElementById('global-loading-bar')) return;
    
    const loadingBar = document.createElement('div');
    loadingBar.id = 'global-loading-bar';
    loadingBar.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #3498db, #2ecc71);
      z-index: 10000;
      animation: progress-indeterminate 1.5s ease-in-out infinite;
      transform-origin: left;
    `;
    
    document.body.appendChild(loadingBar);
  }

  // Ocultar carga global
  hideGlobalLoading() {
    const loadingBar = document.getElementById('global-loading-bar');
    if (loadingBar) {
      loadingBar.style.animation = 'none';
      loadingBar.style.transform = 'scaleX(1)';
      loadingBar.style.transition = 'transform 0.3s ease';
      
      setTimeout(() => {
        loadingBar.remove();
      }, 300);
    }
  }

  // Crear skeleton para tabla de productos
  createProductTableSkeleton(container) {
    const skeleton = document.createElement('div');
    skeleton.className = 'space-y-3';
    skeleton.innerHTML = `
      ${Array.from({length: 8}, () => `
        <div class="flex items-center space-x-4 p-3 border border-gray-200 dark:border-gray-700 rounded">
          <div class="skeleton w-16 h-16 rounded"></div>
          <div class="flex-1 space-y-2">
            <div class="skeleton h-4 w-3/4 rounded"></div>
            <div class="skeleton h-3 w-1/2 rounded"></div>
          </div>
          <div class="skeleton h-8 w-20 rounded"></div>
          <div class="skeleton h-8 w-24 rounded"></div>
        </div>
      `).join('')}
    `;
    
    return skeleton;
  }

  // Crear skeleton para grid de productos (POS)
  createProductGridSkeleton(container) {
    const skeleton = document.createElement('div');
    skeleton.className = 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4';
    skeleton.innerHTML = `
      ${Array.from({length: 12}, () => `
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3">
          <div class="skeleton h-32 w-full rounded"></div>
          <div class="skeleton h-4 w-3/4 rounded"></div>
          <div class="skeleton h-3 w-1/2 rounded"></div>
          <div class="skeleton h-8 w-full rounded"></div>
        </div>
      `).join('')}
    `;
    
    return skeleton;
  }

  // Mostrar loading en un contenedor específico
  showLoading(container, type = 'spinner') {
    if (!container) return;
    
    const existingLoader = container.querySelector('.loading-overlay');
    if (existingLoader) return;
    
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    
    switch (type) {
      case 'skeleton-table':
        container.appendChild(this.createProductTableSkeleton(container));
        return;
        
      case 'skeleton-grid':
        container.appendChild(this.createProductGridSkeleton(container));
        return;
        
      case 'pulse':
        container.classList.add('pulse-loading');
        return;
        
      default:
        overlay.innerHTML = '<div class="spinner"></div>';
        break;
    }
    
    container.style.position = container.style.position || 'relative';
    container.appendChild(overlay);
  }

  // Ocultar loading de un contenedor específico
  hideLoading(container) {
    if (!container) return;
    
    const overlay = container.querySelector('.loading-overlay');
    if (overlay) {
      overlay.remove();
    }
    
    const skeleton = container.querySelector('.skeleton')?.parentElement;
    if (skeleton && skeleton !== container) {
      skeleton.remove();
    }
    
    container.classList.remove('pulse-loading');
  }

  // Mostrar mensaje de carga con progreso
  showProgressMessage(message, progress = null) {
    let messageEl = document.getElementById('progress-message');
    
    if (!messageEl) {
      messageEl = document.createElement('div');
      messageEl.id = 'progress-message';
      messageEl.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        z-index: 10001;
        max-width: 300px;
        backdrop-filter: blur(4px);
      `;
      document.body.appendChild(messageEl);
    }
    
    messageEl.innerHTML = `
      <div style="margin-bottom: 8px;">${message}</div>
      ${progress !== null ? `
        <div class="progress-bar">
          <div class="progress-bar-fill" style="width: ${progress}%"></div>
        </div>
      ` : `
        <div class="progress-bar">
          <div class="progress-bar-fill progress-bar-indeterminate"></div>
        </div>
      `}
    `;
  }

  // Ocultar mensaje de progreso
  hideProgressMessage() {
    const messageEl = document.getElementById('progress-message');
    if (messageEl) {
      messageEl.style.opacity = '0';
      messageEl.style.transition = 'opacity 0.3s ease';
      setTimeout(() => messageEl.remove(), 300);
    }
  }
}

// Instancia global
window.intelligentPreloader = new IntelligentPreloader();

// Funciones de utilidad globales
window.showLoading = function(container, type = 'spinner') {
  window.intelligentPreloader?.showLoading(container, type);
};

window.hideLoading = function(container) {
  window.intelligentPreloader?.hideLoading(container);
};

window.showProgressMessage = function(message, progress = null) {
  window.intelligentPreloader?.showProgressMessage(message, progress);
};

window.hideProgressMessage = function() {
  window.intelligentPreloader?.hideProgressMessage();
};

console.log('✅ Preloader inteligente instalado - Mejorará la percepción de velocidad');
