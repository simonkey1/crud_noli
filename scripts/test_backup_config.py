#!/usr/bin/env python3
"""
Script de prueba para simular el entorno de GitHub Actions
y verificar que la configuración de backup funciona correctamente
"""
import os
import sys
import tempfile
from pathlib import Path

def test_backup_config():
    """Prueba la configuración de backup con diferentes variables de entorno"""
    print("🧪 Probando configuración de backup...")
    
    # Guardar variables originales
    original_env = {
        key: os.environ.get(key) 
        for key in ["DATABASE_URL", "POSTGRES_USER", "POSTGRES_PASSWORD", 
                   "POSTGRES_DB", "POSTGRES_SERVER", "POSTGRES_PORT"]
    }
    
    try:
        # Caso 1: Solo DATABASE_URL (como en GitHub Actions)
        print("\n1️⃣ Probando con solo DATABASE_URL...")
        os.environ.clear()
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
        
        # Recargar módulo
        if 'core.backup_config' in sys.modules:
            del sys.modules['core.backup_config']
        
        from core.backup_config import BackupSettings
        config1 = BackupSettings()
        print(f"   ✅ URL: {config1.get_database_url()}")
        
        # Caso 2: Variables individuales de PostgreSQL
        print("\n2️⃣ Probando con variables PostgreSQL individuales...")
        os.environ.clear()
        os.environ.update({
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass", 
            "POSTGRES_DB": "testdb",
            "POSTGRES_SERVER": "testserver",
            "POSTGRES_PORT": "5432"
        })
        
        # Recargar módulo
        if 'core.backup_config' in sys.modules:
            del sys.modules['core.backup_config']
        
        from core.backup_config import BackupSettings
        config2 = BackupSettings()
        print(f"   ✅ URL: {config2.get_database_url()}")
        
        # Caso 3: Puerto vacío (como en el error)
        print("\n3️⃣ Probando con POSTGRES_PORT vacío...")
        os.environ.clear()
        os.environ.update({
            "POSTGRES_USER": "testuser",
            "POSTGRES_PASSWORD": "testpass",
            "POSTGRES_DB": "testdb", 
            "POSTGRES_SERVER": "testserver",
            "POSTGRES_PORT": ""  # ← Esto causaba el error
        })
        
        # Recargar módulo
        if 'core.backup_config' in sys.modules:
            del sys.modules['core.backup_config']
        
        from core.backup_config import BackupSettings
        config3 = BackupSettings()
        print(f"   ✅ URL: {config3.get_database_url()}")
        print(f"   ✅ Puerto manejado como: {config3.POSTGRES_PORT}")
        
        # Caso 4: Variables vacías (simulando GitHub Actions)
        print("\n4️⃣ Probando con variables vacías...")
        os.environ.clear()
        os.environ.update({
            "DATABASE_URL": "",
            "POSTGRES_USER": "",
            "POSTGRES_PASSWORD": "",
            "POSTGRES_DB": "",
            "POSTGRES_SERVER": "",
            "POSTGRES_PORT": ""
        })
        
        # Recargar módulo
        if 'core.backup_config' in sys.modules:
            del sys.modules['core.backup_config']
        
        from core.backup_config import BackupSettings
        config4 = BackupSettings()
        print(f"   ✅ URL fallback: {config4.get_database_url()}")
        
        print("\n✅ Todos los casos de prueba pasaron!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        return False
        
    finally:
        # Restaurar variables originales
        os.environ.clear()
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value

def test_backup_script():
    """Prueba que el script de backup funcione"""
    print("\n🧪 Probando script de backup...")
    
    try:
        # Recargar módulo con configuración actual
        if 'scripts.backup_database' in sys.modules:
            del sys.modules['scripts.backup_database']
        
        sys.path.append(str(Path(__file__).parent.parent))
        from scripts.backup_database import check_database_status
        
        status = check_database_status()
        print(f"   ✅ Estado de la DB: {status}")
        
        if 'error' in status:
            print(f"   ⚠️ Error de conexión: {status['error']}")
            return False
        else:
            print(f"   ✅ Total de registros: {status.get('total_records', 0)}")
            return True
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Test Suite - Configuración de Backup")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    config_ok = test_backup_config()
    script_ok = test_backup_script()
    
    print("\n📋 Resumen de Pruebas")
    print("=" * 30)
    print(f"✅ Configuración: {'OK' if config_ok else 'ERROR'}")
    print(f"✅ Script de backup: {'OK' if script_ok else 'ERROR'}")
    
    if config_ok and script_ok:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("💡 El sistema de backup está listo para GitHub Actions")
    else:
        print("\n⚠️ Hay problemas que requieren atención")
        
    return config_ok and script_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
