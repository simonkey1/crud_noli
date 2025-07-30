#!/usr/bin/env python
"""
Script para solucionar problemas adicionales de seguridad detectados
Este script complementa fix_security_issues.py para aplicar correcciones adicionales
"""
import os
import sys
import argparse
from sqlalchemy import create_engine, text

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(root_dir)

from core.config import settings

def fix_additional_issues(confirm=False):
    """Ejecuta el script SQL para arreglar problemas adicionales de seguridad y rendimiento"""
    
    # Verificar que estamos en producción
    if settings.ENVIRONMENT != "production":
        print("⚠️ ADVERTENCIA: Este script debe ejecutarse en entorno de producción.")
        print(f"Entorno actual: {settings.ENVIRONMENT}")
        if not confirm:
            answer = input("¿Deseas continuar de todos modos? [s/N]: ")
            if answer.lower() not in ["s", "si", "sí", "y", "yes"]:
                print("Operación cancelada.")
                return False
    
    # Cargar el script SQL
    sql_path = os.path.join(script_dir, "fix_additional_issues.sql")
    if not os.path.exists(sql_path):
        print(f"❌ Error: No se encontró el archivo {sql_path}")
        return False
        
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    # Separar comandos SQL individuales
    sql_commands = sql_script.split(";")
    
    # Conectar a la base de datos
    print(f"🔄 Conectando a la base de datos: {settings.DATABASE_URL}")
    try:
        engine = create_engine(settings.DATABASE_URL, echo=False)
        connection = engine.connect()
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False
    
    # Ejecutar cada comando SQL
    success_count = 0
    error_count = 0
    
    print("🔄 Ejecutando script de corrección adicional...")
    for i, command in enumerate(sql_commands):
        # Saltar líneas vacías y comentarios
        command = command.strip()
        if not command or command.startswith("--"):
            continue
            
        try:
            connection.execute(text(command))
            success_count += 1
        except Exception as e:
            print(f"❌ Error en comando #{i+1}: {str(e)}")
            print(f"Comando: {command[:100]}...")
            error_count += 1
    
    connection.commit()
    connection.close()
    
    # Mostrar resultados
    print(f"✅ Comandos ejecutados exitosamente: {success_count}")
    if error_count > 0:
        print(f"❌ Comandos con error: {error_count}")
        return False
    else:
        print("🎉 Script completado sin errores")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Soluciona problemas adicionales de seguridad en Supabase")
    parser.add_argument("--force", action="store_true", help="Ejecutar sin confirmación incluso en entorno no productivo")
    
    args = parser.parse_args()
    
    if fix_additional_issues(args.force):
        sys.exit(0)
    else:
        sys.exit(1)
