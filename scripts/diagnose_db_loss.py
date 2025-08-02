#!/usr/bin/env python
"""
Script para diagnosticar problemas de pérdida de datos
"""
import os
import sys
import logging
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_diagnostics():
    """Ejecuta diagnósticos básicos para detectar problemas de pérdida de datos"""
    print("🔍 DIAGNÓSTICO DE PROBLEMAS DE PÉRDIDA DE DATOS")
    print("=" * 60)
    
    # 1. Verificar el archivo main.py
    try:
        print("\n🔄 Analizando script de inicio...")
        main_path = os.path.join(root_dir, 'main.py')
        if os.path.exists(main_path):
            print(f"✅ Archivo main.py encontrado en: {main_path}")
            
            with open(main_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar patrones de creación/eliminación de tablas
            drop_all = 'drop_all' in content.lower() or 'dropall' in content.lower()
            create_all = 'create_all' in content.lower() or 'createall' in content.lower()
            
            if drop_all:
                print("⚠️ ALERTA: Se detectó código que podría estar eliminando tablas (drop_all)")
            
            if create_all:
                print("⚠️ ALERTA: Se detectó código que podría estar recreando tablas (create_all)")
                
            # Buscar SQLModel.metadata.create_all
            if 'SQLModel.metadata.create_all' in content:
                print("⚠️ ALERTA: Se detectó 'SQLModel.metadata.create_all' que crea tablas en el arranque")
            
            # Buscar líneas sospechosas
            suspicious_lines = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if any(s in line.lower() for s in ['drop', 'delete', 'truncate', 'purge', 'clear']):
                    suspicious_lines.append((i+1, line.strip()))
            
            if suspicious_lines:
                print("⚠️ Líneas sospechosas encontradas:")
                for line_num, line in suspicious_lines:
                    print(f"   Línea {line_num}: {line}")
            else:
                print("✅ No se encontraron líneas sospechosas en main.py")
        else:
            print(f"❓ No se encontró el archivo main.py en: {main_path}")
    except Exception as e:
        print(f"❌ Error al analizar script de inicio: {str(e)}")
    
    # 2. Verificar base de datos usando credenciales directamente
    try:
        print("\n📡 Intentando verificar configuración de base de datos...")
        # Verificar archivo de configuración
        config_path = os.path.join(root_dir, 'core', 'config.py')
        
        if os.path.exists(config_path):
            print(f"✅ Archivo de configuración encontrado: {config_path}")
            
            # Leer el archivo de configuración
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Buscar indicios de Supabase
            is_supabase = 'supabase' in config_content.lower()
            if is_supabase:
                print("✅ Se detectó configuración para Supabase")
                
                # Verificar si hay cambios en la configuración de entorno
                env_vars = [
                    'DATABASE_URL', 'POSTGRES_USER', 'POSTGRES_PASSWORD',
                    'POSTGRES_SERVER', 'POSTGRES_PORT', 'POSTGRES_DB'
                ]
                
                print("\n🔍 Verificando variables de entorno relevantes:")
                for var in env_vars:
                    if var in os.environ:
                        value = os.environ[var]
                        # Ocultar contraseñas
                        if 'PASSWORD' in var:
                            value = '********'
                        # Truncar URL de base de datos
                        elif 'URL' in var and len(value) > 30:
                            value = value[:20] + '...' + value[-10:]
                        print(f"   - {var}: {value}")
                    else:
                        print(f"   - {var}: No definida")
            
            # Buscar si hay código que reinicia la base de datos en producción
            if 'create_all' in config_content and 'production' in config_content:
                print("⚠️ ALERTA: Posible creación de tablas en entorno de producción")
        else:
            print(f"❓ No se encontró el archivo de configuración en: {config_path}")
    except Exception as e:
        print(f"❌ Error al verificar configuración de base de datos: {str(e)}")
    
    # 3. Verificar configuración de Render
    try:
        print("\n🖥️ Verificando configuración de despliegue...")
        
        # Verificar si estamos en Render
        render_service_id = os.environ.get("RENDER_SERVICE_ID")
        if render_service_id:
            print("✅ Detectado entorno de Render")
            
            # Verificar configuración conocida de Render
            render_path = os.path.join(root_dir, 'render.yaml')
            if os.path.exists(render_path):
                print(f"✅ Archivo de configuración render.yaml encontrado")
                
                with open(render_path, 'r', encoding='utf-8') as f:
                    render_content = f.read()
                
                # Verificar si hay disks (volúmenes persistentes)
                if 'disk:' in render_content:
                    print("✅ Se detectaron configuraciones de discos persistentes")
                else:
                    print("⚠️ No se detectaron configuraciones de discos persistentes")
                    print("   Los datos almacenados fuera de la base de datos podrían perderse")
                
                # Verificar si hay servicios de base de datos
                if 'type: pserv' in render_content or 'type: postgres' in render_content:
                    print("✅ Se detectó configuración de base de datos en Render")
                else:
                    print("ℹ️ No se detectó configuración específica de base de datos en Render")
                    print("   Posiblemente se use un servicio externo como Supabase")
        else:
            # Verificar Dockerfile
            dockerfile_path = os.path.join(root_dir, 'Dockerfile')
            if os.path.exists(dockerfile_path):
                print("✅ Se detectó Dockerfile para despliegue en contenedor")
                
                # Leer Dockerfile
                with open(dockerfile_path, 'r', encoding='utf-8') as f:
                    dockerfile_content = f.read()
                
                # Verificar si hay comandos que podrían reiniciar la base de datos
                if 'alembic upgrade head' in dockerfile_content:
                    print("ℹ️ Se detectó ejecución de migraciones en el Dockerfile (alembic upgrade head)")
                
                if any(cmd in dockerfile_content for cmd in ['python -c', 'python scripts']):
                    print("⚠️ Se detectaron scripts Python que se ejecutan durante el despliegue")
                    print("   Revisa si alguno de estos scripts modifica la base de datos")
    except Exception as e:
        print(f"❌ Error al verificar configuración de despliegue: {str(e)}")
    
    # 4. Recomendaciones generales
    print("\n📋 RECOMENDACIONES PARA EVITAR PÉRDIDA DE DATOS")
    print("=" * 60)
    print("""
1. Problemas comunes en servicios como Render o Supabase:
   - Si usas el plan gratuito de Render, los servicios web se apagan tras 15 minutos de inactividad
   - Al reiniciarse, si la base de datos está en el mismo contenedor, se perderán los datos
   - Supabase tiene políticas RLS que podrían estar bloqueando acceso a los datos

2. Soluciones recomendadas:
   - Asegúrate de que tu base de datos sea un servicio externo persistente
   - Verifica que las credenciales de conexión no cambien entre reinicios
   - En main.py, modifica SQLModel.metadata.create_all para que sea condicional
     (sólo crear tablas si no existen ya)
   - Configura respaldos automáticos y verifica que funcionen

3. Para Supabase específicamente:
   - Verifica que las políticas RLS estén configuradas correctamente
   - Asegúrate de que tu aplicación se conecte con credenciales que tengan permisos
   - Usa el script fix_rls.py para corregir problemas de permisos
   
4. Para Render específicamente:
   - Usa un servicio PostgreSQL dedicado en Render en vez del integrado
   - Configura volúmenes persistentes para almacenar archivos
   - Si necesitas ejecutar migraciones, usa comandos condicionales que no borren datos
    """)

    print("\n✅ Diagnóstico básico completado")
    print("=" * 60)

if __name__ == "__main__":
    run_diagnostics()
