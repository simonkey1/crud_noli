#!/usr/bin/env python
# Script de post-despliegue para restaurar datos desde el backup más reciente
import os
import sys
import logging
import argparse
import datetime

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar funciones necesarias de los scripts existentes
from scripts.verify_backup import list_backups, verify_backup
from scripts.restore_database import restore_backup

# Importar la función para restaurar desde GitHub si están disponibles las variables
try:
    from scripts.github_restore import github_restore
    GITHUB_RESTORE_AVAILABLE = True
except ImportError:
    GITHUB_RESTORE_AVAILABLE = False

# Configurar logging
log_file = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    'logs', 
    'post_deploy.log'
)

# Asegurar que existe el directorio de logs
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def post_deploy_restore(force=False):
    """
    Restaura los datos desde el backup más reciente después de un despliegue.
    
    Args:
        force: Si es True, restaura incluso si hay datos en las tablas.
        
    Returns:
        bool: True si la restauración fue exitosa, False en caso contrario.
    """
    # 1. Verificar si hay datos en las tablas críticas
    from db.database import engine
    from sqlmodel import Session, select, func
    from models.order import Orden, CierreCaja
    
    needs_restore = False
    
    with Session(engine) as session:
        # Verificar tablas críticas
        ordenes_count = session.exec(select(func.count(Orden.id))).one()
        cierres_count = session.exec(select(func.count(CierreCaja.id))).one()
        
        logger.info(f"Estado actual de la base de datos - Órdenes: {ordenes_count}, Cierres: {cierres_count}")
        
        # Determinar si necesitamos restaurar
        if force or (ordenes_count == 0 and cierres_count == 0):
            needs_restore = True
    
    if not needs_restore:
        logger.info("No es necesario restaurar: las tablas ya tienen datos o no se ha forzado la restauración")
        return False
    
    # 2. Obtener la lista de backups disponibles
    backups = list_backups()
    
    if not backups:
        logger.error("No hay backups disponibles para restaurar")
        return False
    
    # 3. Verificar el backup más reciente
    latest_backup = backups[0]
    logger.info(f"Usando el backup más reciente: {latest_backup['id']} ({latest_backup['date']})")
    
    verification = verify_backup(latest_backup["id"])
    if not verification:
        logger.error("No se pudo verificar el backup")
        return False
    
    # Verificar que el backup contiene datos críticos
    transacciones = verification['results'].get('transacciones.json', {})
    cierres = verification['results'].get('cierres_caja.json', {})
    
    if transacciones.get("count", 0) == 0 and cierres.get("count", 0) == 0:
        logger.warning("El backup más reciente no contiene transacciones ni cierres de caja")
        
        # Buscar backup alternativo con datos
        alternative_backup = None
        for backup in backups[1:]:  # Excluir el primero que ya revisamos
            alt_verification = verify_backup(backup["id"])
            if alt_verification:
                alt_transacciones = alt_verification['results'].get('transacciones.json', {})
                alt_cierres = alt_verification['results'].get('cierres_caja.json', {})
                if alt_transacciones.get("count", 0) > 0 or alt_cierres.get("count", 0) > 0:
                    alternative_backup = backup
                    verification = alt_verification
                    break
        
        if alternative_backup:
            logger.info(f"Usando backup alternativo con datos: {alternative_backup['id']}")
            latest_backup = alternative_backup
        else:
            logger.warning("No se encontró ningún backup con transacciones o cierres. Continuando con el más reciente.")
    
    # 4. Restaurar desde el backup seleccionado
    logger.info(f"Iniciando restauración desde backup {latest_backup['id']}")
    success = restore_backup(latest_backup["id"])
    
    if success:
        logger.info(f"Restauración completada con éxito desde {latest_backup['id']}")
        
        # Registrar la restauración en el historial de despliegues
        deploy_history_log = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs',
            'deploy_history.log'
        )
        
        with open(deploy_history_log, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Restauración post-despliegue desde backup {latest_backup['id']}\n")
            
        return True
    else:
        logger.error(f"Error al restaurar desde backup {latest_backup['id']}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Script de post-despliegue para restaurar datos')
    parser.add_argument('--force', action='store_true', help='Forzar restauración incluso si hay datos')
    parser.add_argument('--skip-github', action='store_true', help='Omitir la restauración desde GitHub')
    
    args = parser.parse_args()
    
    logger.info("Iniciando proceso de post-despliegue")
    
    success = False
    
    # Primero intentar restaurar desde GitHub si están disponibles las variables
    github_backup_url = os.environ.get('GITHUB_BACKUP_URL')
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if GITHUB_RESTORE_AVAILABLE and github_backup_url and not args.skip_github:
        logger.info(f"Intentando restaurar desde GitHub: {github_backup_url}")
        try:
            success = github_restore(github_backup_url, github_token, args.force)
            if success:
                logger.info("Restauración desde GitHub completada exitosamente")
                print("✅ Restauración desde GitHub completada exitosamente")
                return 0
            else:
                logger.warning("La restauración desde GitHub no realizó cambios o falló. Intentando restaurar desde backup local.")
        except Exception as e:
            logger.error(f"Error durante la restauración desde GitHub: {str(e)}")
            logger.info("Intentando restaurar desde backup local como alternativa.")
    elif not args.skip_github:
        if not GITHUB_RESTORE_AVAILABLE:
            logger.warning("El módulo de restauración desde GitHub no está disponible.")
        if not github_backup_url:
            logger.warning("No se ha configurado la URL del backup en GitHub (GITHUB_BACKUP_URL).")
        logger.info("Intentando restaurar desde backup local.")
    
    # Si la restauración desde GitHub falla o no está configurada, intentar restaurar desde backup local
    success = post_deploy_restore(args.force)
    
    if success:
        print("✅ Proceso de post-despliegue completado exitosamente")
    else:
        print("❌ El proceso de post-despliegue no realizó cambios o falló")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
