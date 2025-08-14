# core/timezone_utils.py

from datetime import datetime, timezone, timedelta, date
import pytz
from typing import Tuple, Optional

# Zona horaria de Chile
CHILE_TZ = pytz.timezone('America/Santiago')

def get_chile_now() -> datetime:
    """Obtiene la fecha y hora actual en zona horaria de Chile"""
    return datetime.now(CHILE_TZ)

def get_chile_date() -> date:
    """Obtiene la fecha actual en zona horaria de Chile"""
    return get_chile_now().date()

def get_day_bounds_chile(target_date: Optional[date] = None) -> Tuple[datetime, datetime]:
    """
    Obtiene el inicio y fin del día en zona horaria de Chile,
    convertido a UTC para consultas en base de datos
    """
    if target_date is None:
        target_date = get_chile_date()
    
    # Crear inicio y fin del día en zona horaria Chile
    start_chile = CHILE_TZ.localize(datetime.combine(target_date, datetime.min.time()))
    end_chile = CHILE_TZ.localize(datetime.combine(target_date, datetime.max.time()))
    
    # Convertir a UTC para la base de datos
    start_utc = start_chile.astimezone(pytz.UTC).replace(tzinfo=None)
    end_utc = end_chile.astimezone(pytz.UTC).replace(tzinfo=None)
    
    return start_utc, end_utc

def datetime_to_chile_str(dt: datetime) -> str:
    """Convierte datetime UTC a string en zona horaria Chile"""
    if dt is None:
        return "N/A"
    
    if dt.tzinfo is None:
        # Asumir que es UTC si no tiene timezone
        dt = pytz.UTC.localize(dt)
    
    chile_dt = dt.astimezone(CHILE_TZ)
    return chile_dt.strftime('%d/%m/%Y %H:%M')

def format_chile_date(dt: datetime) -> str:
    """Formatea fecha en zona horaria de Chile"""
    if dt is None:
        return "N/A"
    
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    chile_dt = dt.astimezone(CHILE_TZ)
    return chile_dt.strftime('%d/%m/%Y')

def format_chile_time(dt: datetime) -> str:
    """Formatea solo la hora en zona horaria de Chile"""
    if dt is None:
        return "N/A"
    
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    chile_dt = dt.astimezone(CHILE_TZ)
    return chile_dt.strftime('%H:%M')

def utc_to_chile(dt: datetime) -> datetime:
    """Convierte datetime UTC a datetime Chile"""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(CHILE_TZ)

def chile_to_utc(dt: datetime) -> datetime:
    """Convierte datetime Chile a UTC"""
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        dt = CHILE_TZ.localize(dt)
    
    return dt.astimezone(pytz.UTC).replace(tzinfo=None)
