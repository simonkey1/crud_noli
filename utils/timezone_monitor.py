"""
utils/timezone_monitor.py - Monitor para cambios de horario de verano
"""

from datetime import datetime, timedelta
from utils.timezone import now_santiago, TIMEZONE_SANTIAGO
import logging

logger = logging.getLogger(__name__)

def get_timezone_info():
    """
    Obtiene información actual de la zona horaria
    """
    now = now_santiago()
    return {
        "datetime": now,
        "offset_utc": now.utcoffset(),
        "dst_active": now.dst() != timedelta(0),
        "timezone_name": str(now.tzinfo)
    }

def log_timezone_status():
    """
    Registra el estado actual de la zona horaria en los logs
    """
    info = get_timezone_info()
    
    logger.info(f"Timezone Status - "
               f"Time: {info['datetime']}, "
               f"UTC Offset: {info['offset_utc']}, "
               f"DST Active: {info['dst_active']}")
    
    return info

def check_timezone_transition(previous_offset, current_offset):
    """
    Detecta si hubo un cambio de horario y lo registra
    """
    if previous_offset != current_offset:
        logger.warning(f"¡CAMBIO DE HORARIO DETECTADO! "
                      f"De {previous_offset} a {current_offset}")
        return True
    return False

# Función para usar en startup de la aplicación
def initialize_timezone_monitoring():
    """
    Inicializa el monitoreo de zona horaria al arrancar la app
    """
    info = log_timezone_status()
    
    if info['dst_active']:
        logger.info("🌞 Horario de VERANO activo (UTC-3)")
    else:
        logger.info("❄️ Horario de INVIERNO activo (UTC-4)")
    
    return info
