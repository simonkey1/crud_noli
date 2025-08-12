// Optimizador de Formularios - Especialmente para códigos de barras
class FormOptimizer {
  constructor() {
    this.formCache = new Map();
    this.validationCache = new Map();
    this.submitQueue = [];
    this.isSubmitting = false;
    this.autoSaveEnabled = true;
    this.autoSaveInterval = null;
    
    this.init();
    console.log('📝 Optimizador de formularios inicializado');
  }

  // Inicializar optimizador
  init() {
    this.setupFormOptimization();
    this.setupBarcodeOptimization();
    this.setupAutoSave();
    this.setupValidationCache();
  }

  // Configurar optimización de formularios
  setupFormOptimization() {
    // Observar formularios nuevos
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) {
            this.optimizeForms(node);
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Optimizar formularios existentes
    this.optimizeForms(document);
  }

  // Optimizar formularios
  optimizeForms(container) {
    const forms = container.querySelectorAll('form');
    
    forms.forEach(form => {
      if (form.dataset.optimized) return;
      
      form.dataset.optimized = 'true';
      this.enhanceForm(form);
    });
  }

  // Mejorar formulario individual
  enhanceForm(form) {
    // Agregar indicadores de validación en tiempo real
    this.addRealTimeValidation(form);
    
    // Optimizar envío de formulario
    this.optimizeFormSubmission(form);
    
    // Configurar auto-guardado
    this.setupFormAutoSave(form);
    
    // Mejorar campos de código de barras
    this.enhanceBarcodeFields(form);
    
    // Agregar shortcuts de teclado
    this.addFormShortcuts(form);
  }

  // Configurar optimización específica para códigos de barras
  setupBarcodeOptimization() {
    // Detectar campos de código de barras
    const barcodeSelectors = [
      'input[name*="codigo_barra"]',
      'input[name*="barcode"]',
      'input[placeholder*="código"]',
      'input[placeholder*="barcode"]',
      'input[id*="barcode"]'
    ];

    barcodeSelectors.forEach(selector => {
      document.addEventListener('input', (event) => {
        if (event.target.matches(selector)) {
          this.optimizeBarcodeInput(event.target);
        }
      });
    });
  }

  // Optimizar input de código de barras
  optimizeBarcodeInput(input) {
    // Autocompletado inteligente
    this.setupBarcodeAutocomplete(input);
    
    // Validación en tiempo real
    this.validateBarcodeInput(input);
    
    // Sugerencias de formato
    this.showBarcodeFormatHints(input);
    
    // Auto-envío después de completar
    this.setupBarcodeAutoSubmit(input);
  }

  // Configurar autocompletado de códigos de barras
  setupBarcodeAutocomplete(input) {
    if (input.dataset.autocompleteSetup) return;
    input.dataset.autocompleteSetup = 'true';

    let dropdown = input.parentElement.querySelector('.barcode-autocomplete');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.className = 'barcode-autocomplete';
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
    }

    // Manejar entrada de datos
    input.addEventListener('input', () => {
      const value = input.value.trim();
      if (value.length >= 3) {
        this.showBarcodeSuggestions(input, dropdown, value);
      } else {
        dropdown.style.display = 'none';
      }
    });

    // Ocultar dropdown al perder foco
    input.addEventListener('blur', () => {
      setTimeout(() => dropdown.style.display = 'none', 150);
    });
  }

  // Mostrar sugerencias de códigos de barras
  showBarcodeSuggestions(input, dropdown, value) {
    // Obtener códigos de barras recientes del localStorage
    const recentBarcodes = JSON.parse(localStorage.getItem('recent_barcodes') || '[]');
    
    // Filtrar sugerencias
    const suggestions = recentBarcodes
      .filter(barcode => barcode.includes(value))
      .slice(0, 5);

    if (suggestions.length === 0) {
      dropdown.style.display = 'none';
      return;
    }

    dropdown.innerHTML = suggestions.map(suggestion => `
      <div class="barcode-suggestion" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid #eee;">
        <span style="font-family: monospace; font-weight: bold;">${suggestion}</span>
        <span style="opacity: 0.6; margin-left: 8px;">📊</span>
      </div>
    `).join('');

    // Manejar clicks en sugerencias
    dropdown.querySelectorAll('.barcode-suggestion').forEach((item, index) => {
      item.addEventListener('click', () => {
        input.value = suggestions[index];
        input.dispatchEvent(new Event('input'));
        dropdown.style.display = 'none';
        
        // Trigger auto-submit si está configurado
        if (input.dataset.autoSubmit === 'true') {
          setTimeout(() => this.autoSubmitForm(input.form), 500);
        }
      });
    });

    dropdown.style.display = 'block';
  }

  // Validar input de código de barras
  validateBarcodeInput(input) {
    const value = input.value.trim();
    let isValid = true;
    let message = '';

    // Validaciones básicas
    if (value.length > 0) {
      // Verificar que solo contiene números
      if (!/^\d+$/.test(value)) {
        isValid = false;
        message = 'Solo se permiten números';
      }
      
      // Verificar longitud (códigos de barras comunes: 8, 12, 13, 14 dígitos)
      else if (![8, 12, 13, 14].includes(value.length) && value.length > 6) {
        isValid = false;
        message = 'Longitud no estándar';
      }
      
      // Verificar dígito de control para EAN-13
      else if (value.length === 13) {
        if (!this.validateEAN13(value)) {
          isValid = false;
          message = 'Código EAN-13 inválido';
        }
      }
    }

    // Mostrar estado de validación
    this.showValidationState(input, isValid, message);
    
    return isValid;
  }

  // Validar EAN-13
  validateEAN13(barcode) {
    if (barcode.length !== 13) return false;
    
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      const digit = parseInt(barcode[i]);
      sum += (i % 2 === 0) ? digit : digit * 3;
    }
    
    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit === parseInt(barcode[12]);
  }

  // Mostrar estado de validación
  showValidationState(input, isValid, message) {
    // Remover indicadores anteriores
    const existingIndicator = input.parentElement.querySelector('.validation-indicator');
    if (existingIndicator) {
      existingIndicator.remove();
    }

    if (input.value.length === 0) return;

    // Crear indicador
    const indicator = document.createElement('div');
    indicator.className = 'validation-indicator';
    indicator.style.cssText = `
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      z-index: 10;
      font-size: 16px;
    `;

    if (isValid) {
      indicator.textContent = '✅';
      input.style.borderColor = '#22c55e';
    } else {
      indicator.textContent = '❌';
      indicator.title = message;
      input.style.borderColor = '#ef4444';
    }

    const container = input.parentElement;
    if (getComputedStyle(container).position === 'static') {
      container.style.position = 'relative';
    }
    
    container.appendChild(indicator);
  }

  // Configurar auto-envío de formulario para códigos de barras
  setupBarcodeAutoSubmit(input) {
    // Solo si el campo tiene una longitud específica común de códigos de barras
    input.addEventListener('input', () => {
      const value = input.value.trim();
      
      // Auto-enviar para códigos de barras completos
      if ([8, 12, 13, 14].includes(value.length) && this.validateBarcodeInput(input)) {
        // Guardar en códigos recientes
        this.saveToBarcodeHistory(value);
        
        // Auto-enviar después de un breve delay
        setTimeout(() => {
          if (input.value.trim() === value) { // Verificar que no haya cambiado
            this.autoSubmitForm(input.form);
          }
        }, 1000);
      }
    });
  }

  // Guardar en historial de códigos de barras
  saveToBarcodeHistory(barcode) {
    const recent = JSON.parse(localStorage.getItem('recent_barcodes') || '[]');
    
    // Remover si ya existe
    const filtered = recent.filter(b => b !== barcode);
    
    // Agregar al inicio
    filtered.unshift(barcode);
    
    // Mantener solo los últimos 20
    const trimmed = filtered.slice(0, 20);
    
    localStorage.setItem('recent_barcodes', JSON.stringify(trimmed));
  }

  // Auto-enviar formulario
  autoSubmitForm(form) {
    if (!form || this.isSubmitting) return;
    
    // Verificar que todos los campos requeridos estén completos
    const requiredFields = form.querySelectorAll('[required]');
    for (const field of requiredFields) {
      if (!field.value.trim()) {
        console.log('Campo requerido vacío, no auto-enviando');
        return;
      }
    }

    console.log('🚀 Auto-enviando formulario');
    
    // Mostrar indicador
    if (window.showProgressMessage) {
      window.showProgressMessage('Enviando automáticamente...', null);
    }

    // Enviar
    this.isSubmitting = true;
    form.submit();
  }

  // Configurar auto-guardado
  setupFormAutoSave(form) {
    if (!this.autoSaveEnabled) return;
    
    const formId = form.id || `form_${Date.now()}`;
    
    // Cargar datos guardados
    this.loadAutoSavedData(form, formId);
    
    // Configurar guardado automático
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.addEventListener('input', () => {
        this.autoSaveFormData(form, formId);
      });
    });
  }

  // Auto-guardar datos del formulario
  autoSaveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (const [key, value] of formData.entries()) {
      data[key] = value;
    }
    
    localStorage.setItem(`autosave_${formId}`, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  }

  // Cargar datos auto-guardados
  loadAutoSavedData(form, formId) {
    const saved = localStorage.getItem(`autosave_${formId}`);
    if (!saved) return;
    
    try {
      const { data, timestamp } = JSON.parse(saved);
      
      // Solo cargar si es reciente (menos de 1 hora)
      if (Date.now() - timestamp < 3600000) {
        Object.entries(data).forEach(([name, value]) => {
          const field = form.querySelector(`[name="${name}"]`);
          if (field && !field.value) {
            field.value = value;
          }
        });
        
        console.log('📋 Datos del formulario restaurados automáticamente');
      }
    } catch (error) {
      console.warn('Error cargando datos auto-guardados:', error);
    }
  }

  // Agregar shortcuts de teclado a formularios
  addFormShortcuts(form) {
    form.addEventListener('keydown', (event) => {
      // Ctrl/Cmd + Enter para enviar
      if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        event.preventDefault();
        form.submit();
      }
      
      // Escape para limpiar
      if (event.key === 'Escape') {
        const inputs = form.querySelectorAll('input, textarea');
        inputs.forEach(input => {
          if (input.type !== 'hidden' && input.type !== 'submit') {
            input.value = '';
          }
        });
      }
    });
  }

  // Agregar validación en tiempo real
  addRealTimeValidation(form) {
    const inputs = form.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        this.validateField(input);
      });
    });
  }

  // Validar campo individual
  validateField(field) {
    let isValid = true;
    let message = '';
    
    // Validaciones básicas
    if (field.required && !field.value.trim()) {
      isValid = false;
      message = 'Campo requerido';
    } else if (field.type === 'email' && field.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(field.value)) {
        isValid = false;
        message = 'Email inválido';
      }
    } else if (field.type === 'number' && field.value) {
      if (isNaN(field.value)) {
        isValid = false;
        message = 'Debe ser un número';
      }
    }
    
    this.showValidationState(field, isValid, message);
    return isValid;
  }

  // Optimizar envío de formulario
  optimizeFormSubmission(form) {
    form.addEventListener('submit', (event) => {
      // Prevenir doble envío
      if (this.isSubmitting) {
        event.preventDefault();
        return;
      }
      
      this.isSubmitting = true;
      
      // Mostrar indicador de envío
      if (window.showLoading) {
        window.showLoading(form, 'spinner');
      }
      
      // Deshabilitar botón de envío
      const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Enviando...';
        
        // Restaurar después de un tiempo
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText;
          this.isSubmitting = false;
          
          if (window.hideLoading) {
            window.hideLoading(form);
          }
        }, 3000);
      }
      
      // Limpiar auto-guardado después de envío exitoso
      setTimeout(() => {
        const formId = form.id || 'form';
        localStorage.removeItem(`autosave_${formId}`);
      }, 1000);
    });
  }

  // Obtener estadísticas
  getStats() {
    const autoSavedForms = Object.keys(localStorage)
      .filter(key => key.startsWith('autosave_')).length;
    
    const recentBarcodes = JSON.parse(localStorage.getItem('recent_barcodes') || '[]').length;
    
    return {
      optimizedForms: document.querySelectorAll('form[data-optimized="true"]').length,
      autoSavedForms,
      recentBarcodes,
      validationCacheSize: this.validationCache.size
    };
  }

  // Limpiar datos
  clearFormData() {
    // Limpiar auto-guardado
    Object.keys(localStorage)
      .filter(key => key.startsWith('autosave_'))
      .forEach(key => localStorage.removeItem(key));
    
    // Limpiar códigos de barras recientes
    localStorage.removeItem('recent_barcodes');
    
    console.log('🧹 Datos de formularios limpiados');
  }

  // Mostrar/ocultar sugerencias de formato para códigos de barras
  showBarcodeFormatHints(input) {
    const value = input.value.trim();
    let hint = '';
    
    if (value.length > 0) {
      switch (value.length) {
        case 8:
          hint = 'EAN-8 (8 dígitos)';
          break;
        case 12:
          hint = 'UPC-A (12 dígitos)';
          break;
        case 13:
          hint = 'EAN-13 (13 dígitos)';
          break;
        case 14:
          hint = 'GTIN-14 (14 dígitos)';
          break;
        default:
          if (value.length < 8) {
            hint = `${value.length}/8-14 dígitos`;
          }
      }
    }
    
    // Mostrar hint si es útil
    if (hint) {
      let hintElement = input.parentElement.querySelector('.barcode-hint');
      if (!hintElement) {
        hintElement = document.createElement('div');
        hintElement.className = 'barcode-hint';
        hintElement.style.cssText = `
          position: absolute;
          bottom: -20px;
          left: 0;
          font-size: 11px;
          color: #666;
          z-index: 10;
        `;
        
        const container = input.parentElement;
        if (getComputedStyle(container).position === 'static') {
          container.style.position = 'relative';
        }
        
        container.appendChild(hintElement);
      }
      
      hintElement.textContent = hint;
    }
  }
}

// Instancia global
window.formOptimizer = new FormOptimizer();

// Funciones de utilidad globales
window.getFormStats = function() {
  return window.formOptimizer?.getStats();
};

window.clearFormData = function() {
  window.formOptimizer?.clearFormData();
};

window.getRecentBarcodes = function() {
  return JSON.parse(localStorage.getItem('recent_barcodes') || '[]');
};

console.log('✅ Optimizador de formularios instalado - Códigos de barras optimizados');
