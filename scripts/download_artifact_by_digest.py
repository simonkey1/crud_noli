#!/usr/bin/env python3
"""
Script para descargar un artifact específico de GitHub Actions usando su digest
"""
import os
import sys
import requests
import zipfile
from datetime import datetime, timezone
import tempfile
import json

def download_artifact_by_digest(repo_owner, repo_name, digest, github_token):
    """
    Descarga un artifact específico usando su digest SHA256
    """
    print(f"🔍 Buscando artifact con digest: {digest}")
    
    # Obtener lista de artifacts
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/artifacts"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        artifacts_data = response.json()
        artifacts = artifacts_data.get('artifacts', [])
        
        print(f"📦 Encontrados {len(artifacts)} artifacts totales")
        
        # Buscar artifact por digest (necesitamos descargarlo para verificar)
        target_artifact = None
        
        for artifact in artifacts:
            if artifact.get('expired', True):
                continue
                
            # Verificar si es un backup del 13 de agosto (UTC)
            created_at = artifact.get('created_at', '')
            if '2025-08-13' in created_at or '2025-08-14' in created_at:
                print(f"🕒 Artifact candidato: {artifact.get('name')} - {created_at}")
                
                # Intentar descargar para verificar digest
                download_url = artifact.get('archive_download_url')
                if download_url:
                    print(f"📥 Descargando para verificar digest...")
                    
                    download_response = requests.get(download_url, headers=headers)
                    if download_response.status_code == 200:
                        # Calcular digest del contenido
                        import hashlib
                        content_digest = hashlib.sha256(download_response.content).hexdigest()
                        
                        print(f"🔍 Digest calculado: sha256:{content_digest}")
                        
                        if content_digest == digest.replace('sha256:', ''):
                            print(f"✅ ¡Artifact encontrado! {artifact.get('name')}")
                            target_artifact = {
                                'content': download_response.content,
                                'name': artifact.get('name'),
                                'created_at': created_at
                            }
                            break
                    else:
                        print(f"❌ Error descargando: {download_response.status_code}")
        
        if target_artifact:
            # Guardar el artifact
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_13aug_{timestamp}.zip"
            filepath = os.path.join("backups", filename)
            
            os.makedirs("backups", exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(target_artifact['content'])
            
            print(f"💾 Artifact guardado como: {filepath}")
            
            # Verificar contenido
            try:
                with zipfile.ZipFile(filepath, 'r') as zip_file:
                    files = zip_file.namelist()
                    print(f"📋 Contenido del artifact: {files}")
                    
                    if 'manifest.json' in files:
                        manifest_content = zip_file.read('manifest.json').decode('utf-8')
                        manifest = json.loads(manifest_content)
                        print(f"📊 Registros totales: {manifest.get('total_records', 0)}")
                        print(f"🛍️ Productos: {manifest.get('productos', 0)}")
                        print(f"📂 Categorías: {manifest.get('categorias', 0)}")
                        
            except Exception as e:
                print(f"⚠️ Error analizando contenido: {e}")
            
            return filepath
        else:
            print(f"❌ No se encontró artifact con digest {digest}")
            print("📋 Artifacts disponibles del 13-14 agosto:")
            
            for artifact in artifacts:
                if not artifact.get('expired', True):
                    created_at = artifact.get('created_at', '')
                    if '2025-08-13' in created_at or '2025-08-14' in created_at:
                        print(f"  - {artifact.get('name')} - {created_at}")
            
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Función principal"""
    print("🔽 Descargador de Artifact por Digest")
    print("=" * 50)
    
    # Configuración
    repo_owner = "simonkey1"
    repo_name = "crud_noli"
    digest = "sha256:738078e5127b7308a8080451ab79d3bfe68479d8bc7bfefb9746264e43560585"
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not github_token:
        print("❌ Necesitas configurar GITHUB_TOKEN")
        print("💡 Ejecuta: $env:GITHUB_TOKEN='tu_token'")
        return
    
    print(f"📂 Repositorio: {repo_owner}/{repo_name}")
    print(f"🔍 Digest objetivo: {digest}")
    print()
    
    # Descargar artifact
    filepath = download_artifact_by_digest(repo_owner, repo_name, digest, github_token)
    
    if filepath:
        print("\n🎉 ¡Artifact descargado exitosamente!")
        print(f"📁 Ubicación: {filepath}")
        print("\n💡 Para usar este backup:")
        print(f"   python -m scripts.restore_from_backup {os.path.basename(filepath).replace('.zip', '')}")
    else:
        print("\n❌ No se pudo descargar el artifact")

if __name__ == "__main__":
    main()
