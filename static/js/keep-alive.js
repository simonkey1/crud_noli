/**
 * keep-alive.js
 * Script para mantener activa la sesión y evitar modo sleep
 * Pregunta al usuario cada 14 minutos si desea continuar en el sitio
 */

document.addEventListener('DOMContentLoaded', function() {
    // Constantes para los tiempos (en milisegundos)
    // Valores para testing:
    const INACTIVITY_TIMEOUT = 14 * 60 * 1000; // 14 minutos (para testing)
    const PROMPT_TIMEOUT = 60 * 1000; // 10 segundos para responder (para testing)
    
    // Valores para producción (comentados):
    // const INACTIVITY_TIMEOUT = 14 * 60 * 1000; // 14 minutos
    // const PROMPT_TIMEOUT = 60 * 1000; // 1 minuto para responder
    
    // Variables para el control de temporizadores
    let inactivityTimer;
    let promptTimer;
    let modalActive = false;
    
    // Función para crear el modal de confirmación
    function createKeepAliveModal() {
        const modal = document.createElement('div');
        modal.id = 'keep-alive-modal';
        modal.className = 'fixed inset-0 bg-gray-900 bg-opacity-75 z-50 flex items-center justify-center';
        modal.style.display = 'none';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">¿Sigues ahí?</h3>
                    <span class="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs font-medium rounded-md">Modo Prueba</span>
                </div>
                <p class="text-gray-600 dark:text-gray-300 mb-6">
                    Tu sesión está a punto de expirar debido a inactividad. 
                    ¿Deseas continuar en el sitio?
                </p>
                <div class="flex justify-between items-center mb-4">
                    <div class="text-amber-600 dark:text-amber-400 font-medium flex items-center">
                        <svg class="w-5 h-5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span id="keep-alive-countdown">10</span> segundos restantes
                    </div>
                    <div class="flex space-x-3">
                        <button id="keep-alive-cancel" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-md text-gray-800 dark:text-gray-200 transition-colors">
                            Salir
                        </button>
                        <button id="keep-alive-continue" class="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-md transition-colors">
                            Continuar
                        </button>
                    </div>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div id="keep-alive-progress" class="bg-amber-600 h-2 rounded-full" style="width: 100%;"></div>
                </div>
                <div class="mt-2 text-center text-xs text-gray-500 dark:text-gray-400">
                    Tiempo de prueba: 20 segundos de inactividad, 10 segundos para responder
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Configurar los eventos de los botones
        document.getElementById('keep-alive-continue').addEventListener('click', function() {
            continueSession();
        });
        
        document.getElementById('keep-alive-cancel').addEventListener('click', function() {
            closeModal();
        });
        
        return modal;
    }
    
    // Función para mostrar el modal con la animación de la barra de progreso
    function showKeepAlivePrompt() {
        if (modalActive) return;
        
        modalActive = true;
        const modal = document.getElementById('keep-alive-modal') || createKeepAliveModal();
        const progressBar = document.getElementById('keep-alive-progress');
        const countdownElement = document.getElementById('keep-alive-countdown');
        
        // Restablecer la barra de progreso
        progressBar.style.width = '100%';
        modal.style.display = 'flex';
        
        // Duración total en segundos para el contador
        const totalSeconds = Math.floor(PROMPT_TIMEOUT / 1000);
        
        // Animación de la barra de progreso y actualización del contador
        const startTime = Date.now();
        const animate = function() {
            const elapsed = Date.now() - startTime;
            const remaining = PROMPT_TIMEOUT - elapsed;
            
            if (remaining <= 0 || !modalActive) {
                if (modalActive) {
                    // Si el usuario no respondió, cerramos la sesión
                    closeModal();
                }
                return;
            }
            
            // Actualizar la barra de progreso
            const percent = (remaining / PROMPT_TIMEOUT) * 100;
            progressBar.style.width = percent + '%';
            
            // Actualizar el contador de segundos
            const secondsRemaining = Math.ceil(remaining / 1000);
            if (countdownElement && countdownElement.textContent != secondsRemaining) {
                countdownElement.textContent = secondsRemaining;
                
                // Cambiar el color cuando queda poco tiempo
                if (secondsRemaining <= 3) {
                    countdownElement.parentElement.classList.add('text-red-600', 'dark:text-red-400');
                    countdownElement.parentElement.classList.remove('text-amber-600', 'dark:text-amber-400');
                }
            }
            
            requestAnimationFrame(animate);
        };
        
        requestAnimationFrame(animate);
        
        // Establecer un temporizador para cerrar el modal si el usuario no responde
        promptTimer = setTimeout(() => {
            closeModal();
        }, PROMPT_TIMEOUT);
    }
    
    // Función para cerrar el modal
    function closeModal() {
        const modal = document.getElementById('keep-alive-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        modalActive = false;
        clearTimeout(promptTimer);
        
        console.log('[KeepAlive] Sesión cerrada por inactividad o el usuario eligió salir');
        
        // Mostrar notificación de cierre de sesión
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center';
        notification.innerHTML = `
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
            <span>Cerrando sesión por inactividad...</span>
        `;
        document.body.appendChild(notification);
        
        // Redirigir al usuario a la página de login después de mostrar la notificación
        setTimeout(() => {
            // Cerrar sesión y redirigir
            window.location.href = '/auth/logout?redirect=/auth/login&reason=inactivity';
        }, 1500);
    }
    
    // Función para continuar la sesión
    function continueSession() {
        const modal = document.getElementById('keep-alive-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        modalActive = false;
        clearTimeout(promptTimer);
        
        console.log('[KeepAlive] Usuario eligió continuar, enviando petición keep-alive');
        
        // Realizar una petición para mantener la sesión activa
        fetch('/api/keep-alive', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (response.ok) {
                console.log('[KeepAlive] Sesión extendida correctamente');
                return response.json();
            } else {
                console.error('[KeepAlive] Error al extender la sesión', response.status);
                throw new Error('Error en la respuesta del servidor');
            }
        })
        .then(data => {
            console.log('[KeepAlive] Respuesta del servidor:', data);
        })
        .catch(error => {
            console.error('[KeepAlive] Error de red:', error);
        });
        
        // Reiniciar el temporizador de inactividad
        resetInactivityTimer();
    }
    
    // Función para reiniciar el temporizador de inactividad
    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        inactivityTimer = setTimeout(() => {
            console.log('[KeepAlive] Inactividad detectada, mostrando prompt');
            showKeepAlivePrompt();
        }, INACTIVITY_TIMEOUT);
        
        // Solo para testing
        console.log('[KeepAlive] Timer reiniciado, se mostrará el prompt en ' + (INACTIVITY_TIMEOUT/1000) + ' segundos de inactividad');
    }
    
    // Eventos para detectar actividad del usuario
    const activityEvents = [
        'mousedown', 'mousemove', 'keydown',
        'scroll', 'touchstart', 'click', 'keypress'
    ];
    
    // Registrar los eventos para detectar actividad
    activityEvents.forEach(eventType => {
        document.addEventListener(eventType, function() {
            // Solo reiniciamos el temporizador si el modal no está activo
            if (!modalActive) {
                resetInactivityTimer();
            }
        }, true);
    });
    
    // Iniciar el temporizador cuando se carga la página
    resetInactivityTimer();
    
    // Crear el modal al inicio para tenerlo listo
    createKeepAliveModal();
});
