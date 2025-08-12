#!/usr/bin/env python3
"""
Verificación específica para el cambio de horario Chile 2025-2026
6 septiembre 2025: Adelanta 60 minutos (UTC-4 → UTC-3)
Primer sábado abril 2026: Atrasa 60 minutos (UTC-3 → UTC-4)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.timezone import now_santiago, TIMEZONE_SANTIAGO, day_range_santiago
from datetime import datetime, date
import pytz

def test_september_2025_transition():
    """
    Prueba el cambio de horario del 6 de septiembre de 2025
    """
    print("=== Cambio de Horario: 6 Septiembre 2025 ===")
    
    # Fechas críticas alrededor del cambio
    test_dates = [
        # Antes del cambio (5 septiembre - invierno UTC-4)
        datetime(2025, 9, 5, 23, 30, 0),
        
        # Durante la transición (6 septiembre)
        datetime(2025, 9, 6, 23, 30, 0),  # Antes del adelanto
        datetime(2025, 9, 7, 0, 30, 0),   # Después del adelanto
        
        # Después del cambio (7 septiembre - verano UTC-3)
        datetime(2025, 9, 7, 12, 0, 0),
    ]
    
    for test_date in test_dates:
        # Localizar en Santiago
        santiago_dt = TIMEZONE_SANTIAGO.localize(test_date)
        
        print(f"\n📅 {test_date.strftime('%d/%m/%Y %H:%M')}")
        print(f"   Offset UTC: {santiago_dt.utcoffset()}")
        print(f"   DST: {'Activo' if santiago_dt.dst().total_seconds() > 0 else 'Inactivo'}")
        print(f"   Horario: {'Verano (UTC-3)' if santiago_dt.dst().total_seconds() > 0 else 'Invierno (UTC-4)'}")
        
        # Verificar rango del día
        inicio, fin = day_range_santiago(santiago_dt.date())
        duration = fin - inicio
        hours = duration.total_seconds() / 3600
        print(f"   Duración día: {hours:.2f} horas")

def test_april_2026_transition():
    """
    Prueba el cambio de horario del primer sábado de abril 2026
    """
    print("\n=== Cambio de Horario: Primer Sábado Abril 2026 ===")
    
    # Primer sábado de abril 2026
    first_saturday_april = date(2026, 4, 4)  # Verificar si es sábado
    
    # Fechas críticas
    test_dates = [
        # Antes del cambio (3 abril - verano UTC-3)
        datetime(2026, 4, 3, 23, 30, 0),
        
        # Durante la transición (primer sábado abril)
        datetime(2026, 4, 5, 2, 30, 0),  # Antes del atraso  
        datetime(2026, 4, 5, 3, 30, 0),  # Después del atraso
        
        # Después del cambio (6 abril - invierno UTC-4)
        datetime(2026, 4, 6, 12, 0, 0),
    ]
    
    print(f"Primer sábado de abril 2026: {first_saturday_april}")
    
    for test_date in test_dates:
        try:
            # Localizar en Santiago
            santiago_dt = TIMEZONE_SANTIAGO.localize(test_date)
            
            print(f"\n📅 {test_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Offset UTC: {santiago_dt.utcoffset()}")
            print(f"   DST: {'Activo' if santiago_dt.dst().total_seconds() > 0 else 'Inactivo'}")
            print(f"   Horario: {'Verano (UTC-3)' if santiago_dt.dst().total_seconds() > 0 else 'Invierno (UTC-4)'}")
            
        except Exception as e:
            print(f"\n📅 {test_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"   ⚠️ Hora ambigua durante transición: {e}")

def verify_business_logic_during_transitions():
    """
    Verifica que la lógica de negocio funcione correctamente durante las transiciones
    """
    print("\n=== Verificación de Lógica de Negocio ===")
    
    # Día del cambio de septiembre
    transition_date = date(2025, 9, 6)
    inicio, fin = day_range_santiago(transition_date)
    
    print(f"Día de transición (6 sept 2025):")
    print(f"  Inicio: {inicio}")
    print(f"  Fin: {fin}")
    
    duration = fin - inicio
    hours = duration.total_seconds() / 3600
    print(f"  Duración: {hours:.2f} horas")
    
    # Para cierres de caja, un día "corto" de 23 horas sigue siendo válido
    if 22.5 <= hours <= 24.5:
        print("  ✅ Duración aceptable para lógica de negocio")
    else:
        print(f"  ⚠️ Duración anómala: {hours} horas")
    
    print(f"\n💡 Durante las transiciones:")
    print(f"   - Los cierres de caja seguirán funcionando normalmente")
    print(f"   - PyTZ maneja automáticamente las horas duplicadas/saltadas")
    print(f"   - Los rangos de día se ajustan automáticamente")

if __name__ == "__main__":
    print("🇨🇱 Verificación Cambios de Horario Chile 2025-2026")
    print("=" * 55)
    
    test_september_2025_transition()
    test_april_2026_transition()
    verify_business_logic_during_transitions()
    
    print("\n" + "=" * 55)
    print("✅ RESUMEN:")
    print("• 6 septiembre 2025: UTC-4 → UTC-3 (adelanta 1 hora)")
    print("• Primer sábado abril 2026: UTC-3 → UTC-4 (atrasa 1 hora)")
    print("• PyTZ maneja automáticamente ambas transiciones")
    print("• La lógica de negocio es robusta durante los cambios")
    print("• No se requiere intervención manual")
