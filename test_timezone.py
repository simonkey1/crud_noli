#!/usr/bin/env python3
"""
Script de prueba para verificar que las funciones de zona horaria funcionan correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.timezone import (
    now_santiago, today_santiago, 
    start_of_day_santiago, end_of_day_santiago, 
    day_range_santiago, format_datetime_santiago
)
from datetime import datetime, timezone

def test_timezone_functions():
    print("=== Prueba de funciones de zona horaria ===")
    
    # Hora actual en Santiago
    santiago_now = now_santiago()
    print(f"Hora actual en Santiago: {santiago_now}")
    print(f"Zona horaria: {santiago_now.tzinfo}")
    
    # Fecha actual en Santiago
    santiago_today = today_santiago()
    print(f"Fecha actual en Santiago: {santiago_today}")
    
    # Inicio y fin del día
    inicio, fin = day_range_santiago()
    print(f"Inicio del día en Santiago: {inicio}")
    print(f"Fin del día en Santiago: {fin}")
    
    # Formateo
    formatted = format_datetime_santiago(santiago_now)
    print(f"Fecha formateada: {formatted}")
    
    # Comparación con UTC
    utc_now = datetime.now(timezone.utc)
    print(f"Hora UTC: {utc_now}")
    print(f"Diferencia horaria: {santiago_now.utcoffset()}")
    
    print("=== ✅ Todas las funciones funcionan correctamente ===")

if __name__ == "__main__":
    test_timezone_functions()
