"""
utils/timezone.py - Utilidades para manejo de zonas horarias
"""

from datetime import datetime, timezone, date, time
import pytz

# Configuración de zona horaria Santiago de Chile
TIMEZONE_SANTIAGO = pytz.timezone('America/Santiago')

def now_santiago():
    """
    Obtiene la fecha y hora actual en la zona horaria de Santiago de Chile
    """
    return datetime.now(TIMEZONE_SANTIAGO)

def today_santiago():
    """
    Obtiene la fecha actual en la zona horaria de Santiago de Chile
    """
    return now_santiago().date()

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

def start_of_day_santiago(fecha: date = None) -> datetime:
    """
    Obtiene el inicio del día (00:00:00) en la zona horaria de Santiago
    para una fecha específica o la fecha actual
    """
    if fecha is None:
        fecha = today_santiago()
    
    return TIMEZONE_SANTIAGO.localize(datetime.combine(fecha, time.min))

def end_of_day_santiago(fecha: date = None) -> datetime:
    """
    Obtiene el final del día (23:59:59.999999) en la zona horaria de Santiago
    para una fecha específica o la fecha actual
    """
    if fecha is None:
        fecha = today_santiago()
    
    return TIMEZONE_SANTIAGO.localize(datetime.combine(fecha, time.max))

def day_range_santiago(fecha: date = None) -> tuple[datetime, datetime]:
    """
    Retorna una tupla con el inicio y fin del día en la zona horaria de Santiago
    """
    return start_of_day_santiago(fecha), end_of_day_santiago(fecha)
