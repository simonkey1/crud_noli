#!/usr/bin/env python3
"""
Monitor simple para verificar timezone en tiempo real
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from utils.timezone import now_santiago, today_santiago, day_range_santiago
from datetime import datetime
import pytz

def show_current_status():
    """
    Muestra el estado actual del timezone
    """
    ahora = now_santiago()
    hoy = today_santiago()
    inicio_dia, fin_dia = day_range_santiago(hoy)
    
    print("🇨🇱 ESTADO ACTUAL DEL SISTEMA - TIMEZONE SANTIAGO")
    print("=" * 55)
    print(f"⏰ Hora actual Santiago: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📅 Fecha actual: {hoy}")
    print(f"🌍 Offset UTC: {ahora.utcoffset()}")
    print(f"☀️ DST: {'Activo' if ahora.dst().total_seconds() > 0 else 'Inactivo'}")
    print()
    print(f"🕐 Límites del día de hoy:")
    print(f"   Inicio: {inicio_dia}")
    print(f"   Fin: {fin_dia}")
    print()
    
    # Comparar con UTC
    utc_equivalente = ahora.astimezone(pytz.UTC)
    fecha_utc = utc_equivalente.date()
    
    print("⚖️ COMPARACIÓN:")
    print(f"   Fecha Santiago: {hoy}")
    print(f"   Fecha UTC: {fecha_utc}")
    
    if fecha_utc != hoy:
        print(f"   ⚠️ DIFERENCIA: UTC está en {fecha_utc}")
        print(f"   ✅ CORRECCIÓN: Santiago mantiene {hoy}")
    else:
        print(f"   ✅ Ambas fechas coinciden")
    
    print()
    print("💡 PARA VERIFICAR EN PRODUCCIÓN:")
    print("1. Haz una venta de prueba ahora")
    print(f"2. Verifica que aparezca con fecha {hoy}")
    print("3. Comprueba que esté incluida en el cierre de hoy")

if __name__ == "__main__":
    show_current_status()
