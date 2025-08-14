#!/usr/bin/env python3
"""
Script para activar manualmente la restauración automática desde GitHub Actions
"""
import os
import sys
import requests
import json
from datetime import datetime

def trigger_restore_workflow(github_token, repo_owner, repo_name, artifact_name=None, force_restore=False):
    """
    Activa el workflow de restauración automática
    
    Args:
        github_token (str): Token de GitHub con permisos de Actions
        repo_owner (str): Propietario del repositorio (usuario/organización)
        repo_name (str): Nombre del repositorio
        artifact_name (str, optional): Nombre del artifact a usar
        force_restore (bool): Forzar restauración aunque la DB no esté vacía
    """
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/auto-restore.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "ref": "main",  # O la rama que uses por defecto
        "inputs": {}
    }
    
    if artifact_name:
        payload["inputs"]["backup_artifact_name"] = artifact_name
    
    if force_restore:
        payload["inputs"]["force_restore"] = "true"
    
    print(f"🚀 Activando workflow de restauración...")
    print(f"📂 Repositorio: {repo_owner}/{repo_name}")
    print(f"🗂️ Artifact: {artifact_name or 'pre-deploy-backup (default)'}")
    print(f"⚡ Forzar restauración: {'Sí' if force_restore else 'No'}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 204:
            print("✅ ¡Workflow activado exitosamente!")
            print(f"🌐 Puedes monitorear el progreso en: https://github.com/{repo_owner}/{repo_name}/actions")
            return True
        else:
            print(f"❌ Error al activar el workflow: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def get_available_artifacts(github_token, repo_owner, repo_name):
    """
    Lista los artifacts disponibles en el repositorio
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/artifacts"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            artifacts = data.get("artifacts", [])
            
            # Filtrar solo los artifacts de backup
            backup_artifacts = [
                artifact for artifact in artifacts 
                if "backup" in artifact["name"].lower()
            ]
            
            print(f"📦 Se encontraron {len(backup_artifacts)} artifacts de backup:")
            for i, artifact in enumerate(backup_artifacts[:10]):  # Mostrar solo los 10 más recientes
                created_date = datetime.fromisoformat(artifact["created_at"].replace('Z', '+00:00'))
                print(f"  {i+1}. {artifact['name']} - {created_date.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            return backup_artifacts
        else:
            print(f"❌ Error al obtener artifacts: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return []

def main():
    """Función principal con interfaz interactiva"""
    print("🔄 Activador de Restauración Automática")
    print("=" * 40)
    
    # Verificar variables de entorno
    github_token = os.getenv("GITHUB_TOKEN")
    repo_owner = os.getenv("GITHUB_REPO_OWNER", "simonkey1")  # Tu usuario de GitHub
    repo_name = os.getenv("GITHUB_REPO_NAME", "crud_noli")
    
    if not github_token:
        print("❌ No se encontró GITHUB_TOKEN en las variables de entorno")
        print("💡 Crea un token en: https://github.com/settings/tokens")
        print("💡 Necesita permisos: repo, workflow")
        print("💡 Luego ejecuta: export GITHUB_TOKEN=tu_token_aqui")
        return
    
    print(f"📂 Repositorio: {repo_owner}/{repo_name}")
    
    # Preguntar qué hacer
    print("\n¿Qué deseas hacer?")
    print("1. Ver artifacts disponibles")
    print("2. Restaurar usando el backup más reciente")
    print("3. Restaurar usando un artifact específico")
    print("4. Forzar restauración (aunque la DB tenga datos)")
    
    try:
        opcion = input("\nElige una opción (1-4): ").strip()
        
        if opcion == "1":
            print("\n📦 Obteniendo lista de artifacts...")
            get_available_artifacts(github_token, repo_owner, repo_name)
            
        elif opcion == "2":
            print("\n🔄 Activando restauración con backup más reciente...")
            trigger_restore_workflow(github_token, repo_owner, repo_name)
            
        elif opcion == "3":
            artifact_name = input("Nombre del artifact: ").strip()
            if artifact_name:
                print(f"\n🔄 Activando restauración con artifact '{artifact_name}'...")
                trigger_restore_workflow(github_token, repo_owner, repo_name, artifact_name)
            else:
                print("❌ Nombre de artifact no puede estar vacío")
                
        elif opcion == "4":
            artifact_name = input("Nombre del artifact (opcional): ").strip() or None
            print(f"\n⚡ Activando restauración FORZADA...")
            trigger_restore_workflow(github_token, repo_owner, repo_name, artifact_name, force_restore=True)
            
        else:
            print("❌ Opción no válida")
            
    except KeyboardInterrupt:
        print("\n\n👋 Cancelado por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
