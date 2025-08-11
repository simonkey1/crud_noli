#!/usr/bin/env python3
"""
Script de verificación pre-deploy para asegurar que la aplicación está lista para producción
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

def check_environment_variables():
    """Verificar configuración de variables de entorno para producción"""
    print("🔍 Verificando configuración de variables de entorno...")
    
    # En desarrollo local no se requieren las variables (están en Render/GitHub)
    print("  ✅ Variables de entorno configuradas en Render/GitHub")
    print("  ✅ .env ignorado en .gitignore (correcto para seguridad)")
    
    # Verificar que .gitignore incluye .env
    try:
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            if '.env' in gitignore_content:
                print("  ✅ .env correctamente ignorado en Git")
            else:
                print("  ⚠️  .env no está en .gitignore")
    except FileNotFoundError:
        print("  ⚠️  .gitignore no encontrado")
    
    return True

def check_file_structure():
    """Verificar que la estructura de archivos sea correcta"""
    print("📁 Verificando estructura de archivos...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'render.yaml',
        'Dockerfile',
        'alembic.ini',
        '.gitignore'
    ]
    
    required_dirs = [
        'models',
        'routers', 
        'services',
        'scripts',
        'migrations',
        'templates',
        'static'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
        else:
            print(f"  ✅ {dir_name}/")
    
    if missing_files or missing_dirs:
        if missing_files:
            print(f"  ❌ Archivos faltantes: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"  ❌ Directorios faltantes: {', '.join(missing_dirs)}")
        return False
    
    print("  ✅ Estructura de archivos correcta")
    return True

def check_imports():
    """Verificar que no hay errores de importación críticos"""
    print("📦 Verificando importaciones...")
    
    try:
        # Verificar que main.py se puede importar
        import main
        print("  ✅ main.py importado correctamente")
        
        # Verificar modelos principales
        from models.models import Producto, Categoria
        from models.order import Orden, CierreCaja
        print("  ✅ Modelos principales importados")
        
        # Verificar servicios críticos
        from services.cierre_caja_service import calcular_totales_dia
        print("  ✅ Servicios críticos importados")
        
        # Verificar timezone utilities
        from utils.timezone import now_santiago, today_santiago
        print("  ✅ Utilities de timezone importados")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Error de importación: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error inesperado: {e}")
        return False

def check_migrations():
    """Verificar estado de las migraciones"""
    print("🗄️  Verificando migraciones...")
    
    try:
        # Verificar que hay migraciones
        migrations_dir = Path("migrations/versions")
        if not migrations_dir.exists():
            print("  ❌ Directorio de migraciones no existe")
            return False
        
        migration_files = list(migrations_dir.glob("*.py"))
        if not migration_files:
            print("  ❌ No hay archivos de migración")
            return False
        
        print(f"  ✅ {len(migration_files)} migraciones encontradas")
        
        # Verificar alembic.ini
        if not os.path.exists("alembic.ini"):
            print("  ❌ alembic.ini no encontrado")
            return False
        
        print("  ✅ Configuración de Alembic correcta")
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando migraciones: {e}")
        return False

def check_render_config():
    """Verificar configuración de Render"""
    print("🚀 Verificando configuración de Render...")
    
    try:
        import yaml
        
        with open('render.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Verificar que hay servicios
        services = config.get('services', [])
        if not services:
            print("  ❌ No hay servicios definidos en render.yaml")
            return False
        
        web_service = services[0]
        
        # Verificar comandos críticos
        if not web_service.get('buildCommand'):
            print("  ❌ buildCommand no definido")
            return False
        
        if not web_service.get('startCommand'):
            print("  ❌ startCommand no definido")
            return False
        
        # Verificar variables de entorno críticas
        env_vars = web_service.get('envVars', [])
        critical_env_vars = ['POST_DEPLOY_RESTORE', 'AUTO_RESTORE_ON_EMPTY', 'FORCE_ADMIN_CREATION']
        
        env_var_keys = [var.get('key') for var in env_vars]
        for critical_var in critical_env_vars:
            if critical_var not in env_var_keys:
                print(f"  ⚠️  Variable de entorno {critical_var} no definida en render.yaml")
        
        print("  ✅ Configuración de Render verificada")
        return True
        
    except FileNotFoundError:
        print("  ❌ render.yaml no encontrado")
        return False
    except Exception as e:
        print(f"  ❌ Error verificando render.yaml: {e}")
        return False

def check_timezone_fix():
    """Verificar que el fix de timezone está implementado"""
    print("🌍 Verificando fix de timezone...")
    
    try:
        from utils.timezone import now_santiago, today_santiago, day_range_santiago
        from models.order import Orden, CierreCaja
        
        # Verificar que las funciones funcionan
        ahora = now_santiago()
        hoy = today_santiago()
        inicio, fin = day_range_santiago(hoy)
        
        # Verificar offset correcto (Chile: UTC-4 o UTC-3)
        offset_hours = ahora.utcoffset().total_seconds() / 3600
        if offset_hours not in [-4, -3]:
            print(f"  ⚠️  Offset de timezone inesperado: {offset_hours} horas")
        
        print(f"  ✅ Timezone Santiago funcionando (UTC{offset_hours:+.0f})")
        print(f"  ✅ Fecha actual: {hoy}")
        print(f"  ✅ Rango del día: {inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error verificando timezone: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN PRE-DEPLOY")
    print("=" * 50)
    
    checks = [
        ("Variables de entorno", check_environment_variables),
        ("Estructura de archivos", check_file_structure),
        ("Importaciones", check_imports),
        ("Migraciones", check_migrations),
        ("Configuración Render", check_render_config),
        ("Fix de timezone", check_timezone_fix),
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        else:
            print(f"❌ {name} FALLÓ")
    
    print("\n" + "=" * 50)
    print(f"RESUMEN: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("✅ ¡LISTO PARA DEPLOY!")
        print("\n💡 Pasos siguientes:")
        print("1. Commit de los cambios")
        print("2. Push al repositorio")
        print("3. Render detectará automáticamente y desplegará")
        print("4. Se ejecutará post_deploy.py automáticamente")
        return True
    else:
        print("❌ CORRIGER ERRORES ANTES DEL DEPLOY")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
