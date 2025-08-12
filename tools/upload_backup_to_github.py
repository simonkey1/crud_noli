#!/usr/bin/env python3
"""
Script para subir el backup más reciente a GitHub como release
"""

import os
import sys
import zipfile
import json
from pathlib import Path
import subprocess
from datetime import datetime

def find_latest_backup():
    """Encontrar el backup más reciente"""
    backups_dir = Path("backups")
    if not backups_dir.exists():
        print("❌ No se encontró directorio de backups")
        return None
    
    # Buscar archivos ZIP de backup
    zip_files = list(backups_dir.glob("backup_*.zip"))
    if not zip_files:
        print("❌ No se encontraron archivos de backup")
        return None
    
    # Obtener el más reciente por fecha de modificación
    latest_backup = max(zip_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Backup más reciente: {latest_backup.name}")
    
    return latest_backup

def get_backup_info(backup_file):
    """Obtener información del backup"""
    try:
        with zipfile.ZipFile(backup_file, 'r') as zip_ref:
            # Buscar el manifest
            if 'manifest.json' in zip_ref.namelist():
                with zip_ref.open('manifest.json') as manifest_file:
                    manifest = json.load(manifest_file)
                    return manifest
            else:
                # Si no hay manifest, crear información básica
                files = zip_ref.namelist()
                return {
                    "date": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat(),
                    "total_records": 0,
                    "files": files
                }
    except Exception as e:
        print(f"⚠️ Error leyendo backup: {e}")
        return None

def create_release_notes(backup_info, backup_file):
    """Crear las notas del release"""
    notes = f"""# 📦 Backup de Base de Datos

**Archivo**: `{backup_file.name}`
**Fecha**: {backup_info.get('date', 'Desconocida')}
**Registros**: {backup_info.get('total_records', 'N/A')}

## 📋 Contenido

"""
    
    files = backup_info.get('files', [])
    for file in files:
        if file.endswith('.json'):
            notes += f"- `{file}`\n"
    
    notes += f"""
## 🚀 Uso

Este backup puede ser usado automáticamente por el sistema de post-deploy:

1. Configura la variable `GITHUB_BACKUP_URL` en Render
2. El sistema detectará automáticamente cuando la BD esté vacía
3. Restaurará los datos desde este backup

## 📝 Configuración

```bash
GITHUB_BACKUP_URL=https://github.com/simonkey1/crud_noli/releases/download/backup-manual/backup_file.zip
```
"""
    
    return notes

def upload_to_github(backup_file, backup_info):
    """Subir backup a GitHub como release"""
    print("🚀 Subiendo backup a GitHub...")
    
    # Crear tag único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_name = f"backup-manual-{timestamp}"
    
    # Crear notas del release
    notes = create_release_notes(backup_info, backup_file)
    
    # Comando gh para crear release
    cmd = [
        "gh", "release", "create", tag_name,
        str(backup_file),
        "--title", f"Manual Backup - {backup_info.get('date', timestamp)}",
        "--notes", notes
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
        
        if result.returncode == 0:
            print("✅ Backup subido exitosamente a GitHub")
            
            # Extraer URL del release
            lines = result.stdout.split('\n')
            release_url = None
            for line in lines:
                if 'https://github.com' in line and 'releases' in line:
                    release_url = line.strip()
                    break
            
            if release_url:
                print(f"🔗 URL del release: {release_url}")
                
                # Construir URL del archivo
                download_url = f"https://github.com/simonkey1/crud_noli/releases/download/{tag_name}/{backup_file.name}"
                print(f"📥 URL de descarga: {download_url}")
                print()
                print("📋 CONFIGURACIÓN PARA RENDER:")
                print(f"GITHUB_BACKUP_URL={download_url}")
                
                return download_url
            else:
                print("⚠️ No se pudo extraer la URL del release")
                return None
        else:
            print(f"❌ Error subiendo a GitHub: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("❌ GitHub CLI no encontrado. Instala 'gh' para subir automáticamente")
        print("💡 Alternativa: Sube manualmente a GitHub Releases")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("📦 SUBIDA DE BACKUP A GITHUB")
    print("=" * 40)
    
    # Verificar que estamos en el directorio correcto
    if not Path("backups").exists():
        print("❌ Ejecuta este script desde la raíz del proyecto")
        return
    
    # Encontrar backup más reciente
    backup_file = find_latest_backup()
    if not backup_file:
        return
    
    # Obtener información del backup
    backup_info = get_backup_info(backup_file)
    if not backup_info:
        print("❌ No se pudo leer información del backup")
        return
    
    print(f"📊 Información del backup:")
    print(f"  Fecha: {backup_info.get('date', 'Desconocida')}")
    print(f"  Registros: {backup_info.get('total_records', 'N/A')}")
    print(f"  Archivos: {len(backup_info.get('files', []))}")
    print()
    
    # Preguntar confirmación
    response = input("¿Subir este backup a GitHub? (y/N): ")
    if response.lower() not in ['y', 'yes', 's', 'si', 'sí']:
        print("❌ Operación cancelada")
        return
    
    # Subir a GitHub
    download_url = upload_to_github(backup_file, backup_info)
    
    if download_url:
        print("\n🎉 ¡BACKUP SUBIDO EXITOSAMENTE!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Ve a Render Dashboard")
        print("2. Agrega la variable de entorno:")
        print(f"   GITHUB_BACKUP_URL={download_url}")
        print("3. Redeploy para activar la restauración automática")
    else:
        print("\n📝 SUBIDA MANUAL:")
        print("1. Ve a GitHub > Releases")
        print("2. Crea un nuevo release")
        print(f"3. Sube el archivo: {backup_file}")
        print("4. Copia la URL de descarga a GITHUB_BACKUP_URL en Render")

if __name__ == "__main__":
    main()
