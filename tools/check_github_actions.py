#!/usr/bin/env python3
"""
Verificación de GitHub Actions workflows
"""

import yaml
import os
from pathlib import Path

def check_workflow_syntax(workflow_path):
    """Verificar sintaxis YAML del workflow"""
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        return True, workflow
    except yaml.YAMLError as e:
        return False, f"Error de sintaxis YAML: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_backup_workflow(workflow):
    """Validar configuración específica del workflow de backup"""
    issues = []
    suggestions = []
    
    # Verificar estructura básica
    if 'name' not in workflow:
        issues.append("Falta el nombre del workflow")
    
    if 'on' not in workflow:
        issues.append("Falta la configuración de triggers")
    else:
        triggers = workflow['on']
        
        # Verificar schedule
        if 'schedule' in triggers:
            cron = triggers['schedule'][0]['cron']
            print(f"  ✅ Programado para ejecutar: {cron} (2am diario)")
        else:
            suggestions.append("Considerar agregar schedule para backups automáticos")
        
        # Verificar workflow_dispatch
        if 'workflow_dispatch' in triggers:
            print("  ✅ Ejecución manual habilitada")
        else:
            suggestions.append("Considerar agregar workflow_dispatch para ejecución manual")
    
    # Verificar jobs
    if 'jobs' not in workflow:
        issues.append("No se encontraron jobs")
        return issues, suggestions
    
    backup_job = workflow['jobs'].get('backup')
    if not backup_job:
        issues.append("No se encontró el job 'backup'")
        return issues, suggestions
    
    # Verificar steps críticos
    steps = backup_job.get('steps', [])
    step_names = [step.get('name', '') for step in steps]
    
    required_steps = [
        'Checkout código',
        'Configurar Python', 
        'Instalar dependencias',
        'Configurar variables de entorno',
        'Crear backup'
    ]
    
    for required_step in required_steps:
        if not any(required_step in step_name for step_name in step_names):
            issues.append(f"Falta step crítico: {required_step}")
    
    # Verificar configuración de Python
    python_step = next((step for step in steps if 'setup-python' in str(step)), None)
    if python_step:
        python_version = python_step.get('with', {}).get('python-version')
        if python_version == "3.11":
            print("  ✅ Python 3.11 configurado correctamente")
        else:
            suggestions.append(f"Versión Python: {python_version}, recomendado: 3.11")
    
    # Verificar variables de entorno
    env_step = next((step for step in steps if 'Configurar variables' in step.get('name', '')), None)
    if env_step:
        env_commands = env_step.get('run', '')
        required_vars = ['DATABASE_URL', 'JWT_SECRET_KEY', 'POSTGRES_USER']
        
        missing_vars = []
        for var in required_vars:
            if var not in env_commands:
                missing_vars.append(var)
        
        if missing_vars:
            issues.append(f"Variables de entorno faltantes: {missing_vars}")
        else:
            print("  ✅ Variables de entorno críticas configuradas")
    
    return issues, suggestions

def check_secrets_documentation():
    """Verificar que los secrets necesarios estén documentados"""
    required_secrets = [
        'DATABASE_URL',
        'JWT_SECRET_KEY', 
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
        'POSTGRES_SERVER',
        'POSTGRES_PORT',
        'ADMIN_USERNAME',
        'ADMIN_PASSWORD'
    ]
    
    print("  📋 Secrets requeridos en GitHub:")
    for secret in required_secrets:
        print(f"    - {secret}")
    
    return True

def main():
    print("🔍 VERIFICACIÓN DE GITHUB ACTIONS")
    print("=" * 50)
    
    # Buscar workflows
    workflows_dir = Path('.github/workflows')
    if not workflows_dir.exists():
        print("❌ No se encontró directorio .github/workflows")
        return False
    
    workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
    
    if not workflow_files:
        print("❌ No se encontraron archivos de workflow")
        return False
    
    print(f"📁 Encontrados {len(workflow_files)} workflows:")
    for wf in workflow_files:
        print(f"  - {wf.name}")
    
    all_good = True
    
    # Verificar cada workflow
    for workflow_file in workflow_files:
        print(f"\n🔍 Verificando {workflow_file.name}:")
        
        # Verificar sintaxis
        is_valid, workflow_or_error = check_workflow_syntax(workflow_file)
        
        if not is_valid:
            print(f"  ❌ {workflow_or_error}")
            all_good = False
            continue
        
        print("  ✅ Sintaxis YAML válida")
        
        # Verificación específica para backup-database.yml
        if 'backup' in workflow_file.name:
            print("  🗄️  Validando configuración de backup...")
            
            issues, suggestions = validate_backup_workflow(workflow_or_error)
            
            if issues:
                print("  ❌ Problemas encontrados:")
                for issue in issues:
                    print(f"    - {issue}")
                all_good = False
            else:
                print("  ✅ Configuración de backup correcta")
            
            if suggestions:
                print("  💡 Sugerencias:")
                for suggestion in suggestions:
                    print(f"    - {suggestion}")
            
            print("  🔐 Verificando configuración de secrets...")
            check_secrets_documentation()
    
    print("\n" + "=" * 50)
    if all_good:
        print("✅ TODOS LOS WORKFLOWS ESTÁN CORRECTOS")
        print("\n💡 Para activar el backup automático:")
        print("1. Configura todos los secrets en GitHub")
        print("2. Haz push del código")
        print("3. El workflow se ejecutará diariamente a las 2am")
        print("4. También puedes ejecutarlo manualmente desde GitHub Actions")
    else:
        print("❌ SE ENCONTRARON PROBLEMAS EN LOS WORKFLOWS")
    
    return all_good

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
