/**
 * Utilidades para manejo de zona horaria Chile en el frontend
 * static/js/timezone_utils.js
 */

// Zona horaria de Chile
const CHILE_TIMEZONE = 'America/Santiago';

/**
 * Convierte una fecha UTC a zona horaria Chile
 */
function convertToChileTime(utcDateString) {
    if (!utcDateString) return null;
    
    const utcDate = new Date(utcDateString + (utcDateString.includes('Z') ? '' : 'Z'));
    return utcDate.toLocaleString('es-CL', {
        timeZone: CHILE_TIMEZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Obtiene la fecha actual en zona horaria Chile (solo fecha)
 */
function getCurrentChileDate() {
    return new Date().toLocaleDateString('es-CL', {
        timeZone: CHILE_TIMEZONE,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * Formatea fecha para mostrar en la interfaz
 */
function formatChileDateTime(dateString) {
    const chileTime = convertToChileTime(dateString);
    return chileTime ? chileTime.replace(',', ' -') : 'N/A';
}

/**
 * Formatea solo la hora en zona horaria Chile
 */
function formatChileTime(dateString) {
    if (!dateString) return 'N/A';
    
    const utcDate = new Date(dateString + (dateString.includes('Z') ? '' : 'Z'));
    return utcDate.toLocaleTimeString('es-CL', {
        timeZone: CHILE_TIMEZONE,
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Obtiene solo la fecha en formato YYYY-MM-DD para Chile
 */
function getChileDateISO() {
    const now = new Date();
    return now.toLocaleDateString('sv-SE', { // formato ISO pero en zona Chile
        timeZone: CHILE_TIMEZONE
    });
}

/**
 * Aplica conversión de timezone a elementos con data-utc-time
 */
function applyChileTimezone() {
    document.querySelectorAll('[data-utc-time]').forEach(element => {
        const utcTime = element.getAttribute('data-utc-time');
        const chileTime = formatChileTime(utcTime);
        element.textContent = chileTime;
    });
    
    document.querySelectorAll('[data-utc-datetime]').forEach(element => {
        const utcDateTime = element.getAttribute('data-utc-datetime');
        const chileDateTime = formatChileDateTime(utcDateTime);
        element.textContent = chileDateTime;
    });
}

// Exportar funciones para uso global
window.ChileTime = {
    convert: convertToChileTime,
    getCurrentDate: getCurrentChileDate,
    format: formatChileDateTime,
    formatTime: formatChileTime,
    getDateISO: getChileDateISO,
    apply: applyChileTimezone
};

// Aplicar automáticamente al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    applyChileTimezone();
});
