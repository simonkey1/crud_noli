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
logger = logging.getLogger(__name__)"

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, 'logs', 'diagnostico.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Verifica la conexión a la base de datos y sus detalles"""
    try:
        print(f"\n📡 Verificando conexión a la base de datos...")
        print(f"URL: {settings.DATABASE_URL.replace(settings.POSTGRES_PASSWORD, '********')}")
        print(f"Ambiente: {settings.ENVIRONMENT}")
        
        # Probar la conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            print(f"✅ Conexión exitosa a PostgreSQL versión: {result[0]}")
            
            # Verificar tamaño de la base de datos
            result = conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)).fetchone()
            print(f"📊 Tamaño de la base de datos: {result[0]}")
            
            # Verificar estadísticas de tablas
            result = conn.execute(text("""
                SELECT 
                    relname as tabla, 
                    n_live_tup as registros
                FROM 
                    pg_stat_user_tables 
                ORDER BY 
                    n_live_tup DESC
            """)).fetchall()
            
            print("\n📋 Estadísticas de tablas:")
            for row in result:
                print(f"   - {row[0]}: {row[1]} registros")
                
        return True
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False

def check_rls_settings():
    """Verifica la configuración de Row Level Security"""
    try:
        print("\n🔒 Verificando configuración de Row Level Security (RLS)...")
        
        with engine.connect() as conn:
            # Verificar tablas con RLS habilitado
            result = conn.execute(text("""
                SELECT 
                    tablename,
                    rowsecurity 
                FROM 
                    pg_tables
                WHERE 
                    schemaname = 'public'
                ORDER BY 
                    tablename
            """)).fetchall()
            
            print("\n📋 Estado de RLS por tabla:")
            for row in result:
                status = "✅ Habilitado" if row[1] else "❌ Deshabilitado"
                print(f"   - {row[0]}: {status}")
            
            # Verificar políticas de RLS
            result = conn.execute(text("""
                SELECT 
                    tablename,
                    policyname,
                    permissive,
                    cmd
                FROM 
                    pg_policies 
                WHERE 
                    schemaname = 'public'
                ORDER BY 
                    tablename, policyname
            """)).fetchall()
            
            print("\n📋 Políticas de RLS configuradas:")
            for row in result:
                permissive = "Permisiva" if row[2] else "Restrictiva"
                print(f"   - {row[0]}: {row[1]} ({row[3]}, {permissive})")
                
        return True
    except Exception as e:
        print(f"❌ Error al verificar configuración de RLS: {str(e)}")
        return False

def check_data_access():
    """Verifica el acceso a los datos según las políticas"""
    try:
        print("\n🔍 Verificando acceso a los datos...")
        
        with Session(engine) as session:
            # Verificar categorías
            categorias = session.exec(select(Categoria)).all()
            print(f"📋 Categorías accesibles: {len(list(categorias))}")
            
            # Verificar productos
            productos = session.exec(select(Producto)).all()
            print(f"📋 Productos accesibles: {len(list(productos))}")
            
            # Mostrar ejemplos de datos
            if productos:
                print("\n📝 Ejemplos de productos accesibles:")
                for i, producto in enumerate(productos[:5]):
                    print(f"   {i+1}. {producto.nombre} (ID: {producto.id})")
            else:
                print("❌ No se encontraron productos accesibles")
                
        return True
    except Exception as e:
        print(f"❌ Error al verificar acceso a los datos: {str(e)}")
        return False

def check_render_config():
    """Verifica la configuración de Render si es posible"""
    try:
        print("\n🖥️ Verificando configuración de Render...")
        render_service_id = os.environ.get("RENDER_SERVICE_ID")
        
        if render_service_id:
            print(f"✅ Servicio Render detectado: {render_service_id}")
            
            # Verificar variables de entorno relevantes de Render
            render_vars = {k: v for k, v in os.environ.items() if k.startswith("RENDER_")}
            print(f"📋 Variables de entorno de Render detectadas: {len(render_vars)}")
            
            # Verificar configuración de persistencia
            print("\n⚠️ Recomendaciones para Render:")
            print("   1. Asegúrate de que los directorios que necesitan persistencia estén montados como volúmenes")
            print("   2. Verifica que la base de datos sea un servicio externo (no en el mismo contenedor)")
            print("   3. Revisa los logs de Render para ver si hay errores durante el despliegue")
        else:
            print("ℹ️ No se detectó que esta aplicación esté corriendo en Render")
            
        return True
    except Exception as e:
        print(f"❌ Error al verificar configuración de Render: {str(e)}")
        return False

def check_deployment_history():
    """Analiza el historial de despliegues si está disponible"""
    try:
        deploy_log = os.path.join(root_dir, 'logs', 'deploy_history.log')
        
        print("\n📜 Verificando historial de despliegues...")
        if os.path.exists(deploy_log):
            with open(deploy_log, 'r') as f:
                history = f.readlines()
                print(f"✅ Historial de despliegues encontrado con {len(history)} entradas")
                if history:
                    print("📋 Últimos despliegues:")
                    for line in history[-5:]:
                        print(f"   - {line.strip()}")
        else:
            print("ℹ️ No se encontró historial de despliegues")
            
            # Crear archivo de historial para futuros despliegues
            os.makedirs(os.path.dirname(deploy_log), exist_ok=True)
            with open(deploy_log, 'w') as f:
                f.write(f"{datetime.now().isoformat()} - Primer registro de diagnóstico\n")
            print("✅ Se ha creado un archivo de historial para futuros despliegues")
            
        return True
    except Exception as e:
        print(f"❌ Error al verificar historial de despliegues: {str(e)}")
        return False

def create_watchdog():
    """Crea un script de vigilancia para detectar cambios en la base de datos"""
    try:
        print("\n🔍 Creando script de vigilancia (watchdog)...")
        
        watchdog_path = os.path.join(script_dir, 'db_utils', 'data_watchdog.py')
        
        if not os.path.exists(os.path.dirname(watchdog_path)):
            os.makedirs(os.path.dirname(watchdog_path))
        
        watchdog_code = """#!/usr/bin/env python
# Script para monitorear cambios en la base de datos
import os
import sys
import time
import json
import logging
from datetime import datetime

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(root_dir)

from db.database import engine
from sqlmodel import Session, select
from sqlalchemy import text
from models.models import Producto, Categoria

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(root_dir, 'logs', 'data_watchdog.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def count_records():
    # Cuenta los registros en las principales tablas"""
    counts = {}
    try:
        with Session(engine) as session:
            # Contar productos
            productos_count = session.exec(select(Producto)).all()
            counts['productos'] = len(list(productos_count))
            
            # Contar categorías
            categorias_count = session.exec(select(Categoria)).all()
            counts['categorias'] = len(list(categorias_count))
            
        return counts
    except Exception as e:
        logger.error(f"Error al contar registros: {str(e)}")
        return {'error': str(e)}

def save_snapshot(counts):
    """Guarda una instantánea de los conteos en un archivo JSON"""
    snapshots_dir = os.path.join(root_dir, 'logs', 'snapshots')
    if not os.path.exists(snapshots_dir):
        os.makedirs(snapshots_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_file = os.path.join(snapshots_dir, f"snapshot_{timestamp}.json")
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'counts': counts
    }
    
    with open(snapshot_file, 'w') as f:
        json.dump(data, f, indent=2)
        
    logger.info(f"Instantánea guardada en {snapshot_file}")
    
    # También actualizar el último estado
    latest_file = os.path.join(snapshots_dir, "latest_state.json")
    with open(latest_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return snapshot_file

def compare_with_previous():
    """Compara el estado actual con el anterior"""
    latest_file = os.path.join(root_dir, 'logs', 'snapshots', "latest_state.json")
    
    if not os.path.exists(latest_file):
        logger.info("No hay estado anterior para comparar")
        return None
        
    try:
        with open(latest_file, 'r') as f:
            previous_data = json.load(f)
            
        current_counts = count_records()
        
        changes = {}
        for key in set(previous_data['counts'].keys()).union(current_counts.keys()):
            prev_count = previous_data['counts'].get(key, 0)
            curr_count = current_counts.get(key, 0)
            
            if prev_count != curr_count:
                changes[key] = {
                    'before': prev_count,
                    'after': curr_count,
                    'diff': curr_count - prev_count
                }
                
        if changes:
            logger.warning(f"Cambios detectados en los datos: {changes}")
            
            # Registrar la alerta en un archivo especial
            alert_file = os.path.join(root_dir, 'logs', 'data_changes_alert.log')
            with open(alert_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} - Cambios detectados: {json.dumps(changes)}\\n")
                
        return changes
    except Exception as e:
        logger.error(f"Error al comparar estados: {str(e)}")
        return None

def run_monitor(interval=3600):
    """Ejecuta el monitor cada cierto intervalo (en segundos)"""
    logger.info(f"Iniciando monitoreo de datos cada {interval} segundos")
    
    try:
        # Tomar primera instantánea
        counts = count_records()
        save_snapshot(counts)
        logger.info(f"Estado inicial guardado: {counts}")
        
        while True:
            time.sleep(interval)
            logger.info("Tomando nueva instantánea...")
            
            counts = count_records()
            save_snapshot(counts)
            
            changes = compare_with_previous()
            if changes:
                logger.warning(f"⚠️ ALERTA: Se detectaron cambios en los datos: {changes}")
            else:
                logger.info("✅ No se detectaron cambios en los datos")
    
    except KeyboardInterrupt:
        logger.info("Monitoreo detenido manualmente")
    except Exception as e:
        logger.error(f"Error en el monitoreo: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor de cambios en datos')
    parser.add_argument('--interval', type=int, default=3600, 
                        help='Intervalo entre verificaciones (segundos)')
    parser.add_argument('--snapshot', action='store_true',
                        help='Tomar una instantánea y salir')
    
    args = parser.parse_args()
    
    if args.snapshot:
        counts = count_records()
        snapshot_file = save_snapshot(counts)
        print(f"Instantánea guardada en {snapshot_file}")
        print(f"Estado actual: {counts}")
    else:
        run_monitor(args.interval)
"""
        
        with open(watchdog_path, 'w') as f:
            f.write(watchdog_code)
            
        print(f"✅ Script de vigilancia creado en: {watchdog_path}")
        print("""
    Para usar el script de vigilancia:
    1. Para tomar una instantánea del estado actual:
       python scripts/db_utils/data_watchdog.py --snapshot
       
    2. Para iniciar el monitor continuo (cada hora):
       python scripts/db_utils/data_watchdog.py
       
    3. Para personalizar el intervalo (ej: cada 10 minutos):
       python scripts/db_utils/data_watchdog.py --interval 600
    """)
            
        return True
    except Exception as e:
        print(f"❌ Error al crear script de vigilancia: {str(e)}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Diagnóstico de problemas de pérdida de datos')
    parser.add_argument('--create-watchdog', action='store_true', help='Crear script de vigilancia')
    parser.add_argument('--check-rls', action='store_true', help='Verificar configuración de Row Level Security')
    parser.add_argument('--all', action='store_true', help='Ejecutar todas las verificaciones')
    
    args = parser.parse_args()
    
    print("🔍 DIAGNÓSTICO DE PROBLEMAS DE PÉRDIDA DE DATOS")
    print("=" * 60)
    
    # Ejecutar verificaciones según argumentos
    if args.all or not (args.create_watchdog or args.check_rls):
        check_database_connection()
        check_data_access()
        check_rls_settings()
        check_render_config()
        check_deployment_history()
        create_watchdog()
    else:
        if args.check_rls:
            check_rls_settings()
        
        if args.create_watchdog:
            create_watchdog()
    
    print("\n✅ Diagnóstico completado")
    print("=" * 60)
    print("""
Recomendaciones para evitar pérdida de datos:
1. Configura backups automáticos en Supabase o con el sistema existente
2. Verifica las políticas de Row Level Security (RLS)
3. Usa el script de vigilancia para detectar cambios inesperados
4. En Render, configura volúmenes persistentes si necesitas almacenar archivos
5. Revisa los logs de despliegue después de cada actualización
    """)

if __name__ == "__main__":
    # Crear directorio de logs si no existe
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    main()
