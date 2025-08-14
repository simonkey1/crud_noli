#!/usr/bin/env python3
"""
Script de configuración rápida para el sistema de restauración automática
"""
import os
import sys
import json
from pathlib import Path

def create_github_token_file():
    """Crea un archivo para almacenar el token de GitHub de forma segura"""
    print("🔐 Configuración del Token de GitHub")
    print("=" * 40)
    print()
    print("Para usar el sistema de restauración automática necesitas un token personal de GitHub.")
    print()
    print("📋 Pasos:")
    print("1. Ve a: https://github.com/settings/tokens")
    print("2. Click en 'Generate new token (classic)'")
    print("3. Selecciona estos permisos:")
    print("   ✓ repo (Full control of private repositories)")
    print("   ✓ workflow (Update GitHub Action workflows)")
    print("4. Genera el token y cópialo")
    print()
    
    token = input("Pega tu token aquí (o presiona Enter para omitir): ").strip()
    
    if token:
        # Crear archivo .env local para el token
        env_file = Path(".env.local")
        
        if env_file.exists():
            content = env_file.read_text()
            if "GITHUB_TOKEN=" in content:
                print("⚠️ Ya existe un GITHUB_TOKEN en .env.local")
                overwrite = input("¿Sobreescribir? (s/N): ").lower().startswith('s')
                if not overwrite:
                    print("Token no actualizado.")
                    return
        
        with open(env_file, "w") as f:
            f.write(f"GITHUB_TOKEN={token}\n")
        
        print(f"✅ Token guardado en {env_file}")
        print("💡 Puedes cargarlo con: source .env.local")
    else:
        print("⏭️ Token omitido. Configúralo manualmente con:")
        print("   export GITHUB_TOKEN=tu_token_aqui")

def check_workflows():
    """Verifica que los workflows estén en su lugar"""
    print("\n🔍 Verificando workflows de GitHub Actions...")
    
    workflows_dir = Path(".github/workflows")
    required_workflows = [
        "auto-restore.yml",
        "ci-cd.yml"
    ]
    
    missing_workflows = []
    
    for workflow in required_workflows:
        workflow_path = workflows_dir / workflow
        if workflow_path.exists():
            print(f"✅ {workflow} - Encontrado")
        else:
            print(f"❌ {workflow} - Faltante")
            missing_workflows.append(workflow)
    
    if missing_workflows:
        print(f"\n⚠️ Faltan {len(missing_workflows)} workflows")
        print("💡 Ejecuta este script desde la raíz del repositorio")
        return False
    else:
        print("✅ Todos los workflows están configurados")
        return True

def check_scripts():
    """Verifica que los scripts estén disponibles"""
    print("\n🔍 Verificando scripts de restauración...")
    
    scripts_dir = Path("scripts")
    required_scripts = [
        "trigger_restore.py",
        "trigger_restore.ps1",
        "backup_database.py"
    ]
    
    missing_scripts = []
    
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"✅ {script} - Encontrado")
        else:
            print(f"❌ {script} - Faltante")
            missing_scripts.append(script)
    
    if missing_scripts:
        print(f"\n⚠️ Faltan {len(missing_scripts)} scripts")
        return False
    else:
        print("✅ Todos los scripts están disponibles")
        return True

def show_usage_examples():
    """Muestra ejemplos de uso"""
    print("\n📚 Ejemplos de Uso")
    print("=" * 40)
    print()
    print("1. 🐍 Python (Multiplataforma):")
    print("   python scripts/trigger_restore.py")
    print()
    print("2. 🔷 PowerShell (Windows):")
    print("   .\\scripts\\trigger_restore.ps1")
    print()
    print("3. 🌐 GitHub Actions (Web):")
    print("   Ve a: https://github.com/simonkey1/crud_noli/actions")
    print("   Busca: 'Auto Restore from Backup'")
    print("   Click: 'Run workflow'")
    print()
    print("4. 📡 API (curl):")
    print("   curl -X POST \\")
    print("     -H 'Accept: application/vnd.github.v3+json' \\")
    print("     -H 'Authorization: token TU_TOKEN' \\")
    print("     -d '{\"ref\":\"main\",\"inputs\":{\"force_restore\":\"true\"}}' \\")
    print("     https://api.github.com/repos/simonkey1/crud_noli/actions/workflows/auto-restore.yml/dispatches")

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    print("\n🔍 Probando conexión a la base de datos...")
    
    try:
        sys.path.append(str(Path(__file__).parent.parent))
        from scripts.backup_database import check_database_status
        
        status = check_database_status()
        
        if 'error' in status:
            print(f"❌ Error de conexión: {status['error']}")
            return False
        else:
            print("✅ Conexión exitosa")
            print(f"📊 Total de registros: {status.get('total_records', 0)}")
            
            for table, count in status.items():
                if table not in ['total_records', 'error']:
                    print(f"   {table}: {count}")
            
            return True
            
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de estar en la raíz del proyecto")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Configurador del Sistema de Restauración Automática")
    print("=" * 60)
    print()
    
    # Verificar que estamos en la raíz del proyecto
    if not Path("main.py").exists():
        print("❌ Este script debe ejecutarse desde la raíz del proyecto (donde está main.py)")
        sys.exit(1)
    
    print("📍 Proyecto: CRUD Noli - Sistema POS")
    print("🔗 Repositorio: https://github.com/simonkey1/crud_noli")
    print()
    
    # Verificaciones
    workflows_ok = check_workflows()
    scripts_ok = check_scripts()
    
    if not workflows_ok or not scripts_ok:
        print("\n❌ Configuración incompleta")
        print("💡 Asegúrate de que todos los archivos estén presentes")
        sys.exit(1)
    
    # Configurar token
    create_github_token_file()
    
    # Probar conexión a la base de datos
    db_ok = test_database_connection()
    
    # Mostrar ejemplos de uso
    show_usage_examples()
    
    # Resumen final
    print("\n📋 Resumen de Configuración")
    print("=" * 40)
    print(f"✅ Workflows: {'OK' if workflows_ok else 'ERROR'}")
    print(f"✅ Scripts: {'OK' if scripts_ok else 'ERROR'}")
    print(f"✅ Base de Datos: {'OK' if db_ok else 'ERROR'}")
    print()
    
    if workflows_ok and scripts_ok and db_ok:
        print("🎉 ¡Sistema configurado correctamente!")
        print("💡 Ya puedes usar cualquiera de los métodos de restauración")
    else:
        print("⚠️ Hay problemas en la configuración")
        print("💡 Revisa los errores mostrados arriba")
    
    print("\n📖 Documentación completa:")
    print("   docs/sistema_restauracion_automatica.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
