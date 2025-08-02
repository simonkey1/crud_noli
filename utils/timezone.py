"""
utils/timezone.py - Utilidades para manejo de zonas horarias
"""

from datetime import datetime, timezone
import pytz

# Configuración de zona horaria Santiago de Chile
TIMEZONE_SANTIAGO = pytz.timezone('America/Santiago')

def now_santiago():
    """
    Obtiene la fecha y hora actual en la zona horaria de Santiago de Chile
    """
    return datetime.now(TIMEZONE_SANTIAGO)

def utcnow_with_timezone():
    """
    Obtiene la fecha y hora UTC actual con información de zona horaria
    """
    return datetime.now(timezone.utc)

def convert_to_santiago(dt):
    """
    Convierte una fecha y hora a la zona horaria de Santiago
    Si la fecha no tiene información de zona horaria, se asume UTC
    """
    if dt.tzinfo is None:
        # Si no tiene información de zona horaria, asumimos que es UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TIMEZONE_SANTIAGO)

def format_datetime_santiago(dt, format="%d/%m/%Y %H:%M"):
    """
    Formatea una fecha y hora a la zona horaria de Santiago con el formato especificado
    """
    santiago_dt = convert_to_santiago(dt)
    return santiago_dt.strftime(format)
