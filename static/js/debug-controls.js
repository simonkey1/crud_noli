// Controlador para los botones de debug en el header
document.addEventListener('DOMContentLoaded', function() {
  const debugControls = document.getElementById('debug-controls');
  const debugMenuBtn = document.getElementById('debug-menu-btn');
  const debugDropdown = document.getElementById('debug-dropdown');
  
  // Mostrar/ocultar controles de debug según el estado
  function updateDebugControlsVisibility() {
    const isDebugEnabled = localStorage.getItem('global_debug') === 'true';
    
    if (debugControls) {
      if (isDebugEnabled) {
        debugControls.classList.remove('hidden');
      } else {
        debugControls.classList.add('hidden');
      }
    }
  }
  
  // Configurar funcionalidad del menú desplegable
  if (debugMenuBtn && debugDropdown) {
    debugMenuBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      debugDropdown.classList.toggle('hidden');
    });
    
    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', function() {
      if (debugDropdown) {
        debugDropdown.classList.add('hidden');
      }
    });
    
    // Prevenir que los clicks en el dropdown lo cierren
    debugDropdown.addEventListener('click', function(e) {
      e.stopPropagation();
    });
  }
  
  // Verificar estado inicial
  updateDebugControlsVisibility();
  
  // Escuchar cambios en localStorage para mostrar/ocultar los controles
  window.addEventListener('storage', updateDebugControlsVisibility);
  
  // También verificar periódicamente (en caso de cambios en la misma pestaña)
  setInterval(updateDebugControlsVisibility, 1000);
  
  // Funciones globales para los botones
  window.debugControlsModule = {
    clearCurrentSessionWithConfirm: function() {
      if (confirm('¿Limpiar métricas de la sesión actual?')) {
        window.universalMonitor?.clearCurrentSession?.();
        debugDropdown?.classList.add('hidden');
      }
    },
    
    clearAllWithConfirm: function() {
      if (confirm('⚠️ ¿Limpiar TODO el historial de métricas? Esta acción no se puede deshacer.')) {
        window.universalMonitor?.clearAll?.();
        debugDropdown?.classList.add('hidden');
      }
    },
    
    exportMetrics: function() {
      window.universalMonitor?.export?.();
      debugDropdown?.classList.add('hidden');
    },
    
    togglePanel: function() {
      window.universalMonitor?.toggle?.();
      debugDropdown?.classList.add('hidden');
    },
    
    showHistory: function() {
      window.debugHistory?.();
      debugDropdown?.classList.add('hidden');
    },
    
    disableDebugWithConfirm: function() {
      if (confirm('¿Desactivar el monitor de performance?')) {
        window.disableDebug?.();
        debugDropdown?.classList.add('hidden');
      }
    }
  };
});

// Funciones para usar desde onclick en el HTML
function clearCurrentSessionConfirm() {
  window.debugControlsModule?.clearCurrentSessionWithConfirm?.();
}

function clearAllConfirm() {
  window.debugControlsModule?.clearAllWithConfirm?.();
}

function exportMetricsFromButton() {
  window.debugControlsModule?.exportMetrics?.();
}

function togglePanelFromButton() {
  window.debugControlsModule?.togglePanel?.();
}

function showHistoryFromButton() {
  window.debugControlsModule?.showHistory?.();
}

function disableDebugConfirm() {
  window.debugControlsModule?.disableDebugWithConfirm?.();
}
