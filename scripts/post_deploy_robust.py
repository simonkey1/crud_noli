#!/usr/bin/env python
"""
Script mejorado de post-deploy que usa la restauración robusta con mapeo de IDs
"""
import os
import sys
import logging
import json
import requests
import zipfile
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session, select, text
from models.models import Producto, Categoria
from models.order import Orden

# Configurar logging
log_file = Path(__file__).parent.parent / 'logs' / 'post_deploy.log'
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_database_empty():
    """Verifica si la base de datos está vacía"""
    with Session(engine) as session:
        categorias_count = len(session.exec(select(Categoria)).all())
        productos_count = len(session.exec(select(Producto)).all())
        ordenes_count = len(session.exec(select(Orden)).all())
        
        is_empty = categorias_count == 0 and productos_count == 0 and ordenes_count == 0
        
        logger.info(f"Estado de la base de datos:")
        logger.info(f"  Categorías: {categorias_count}")
        logger.info(f"  Productos: {productos_count}")
        logger.info(f"  Órdenes: {ordenes_count}")
        logger.info(f"  Está vacía: {is_empty}")
        
        return is_empty

def download_github_backup():
    """Descarga el backup más reciente desde GitHub Releases"""
    github_token = os.getenv('GITHUB_TOKEN')
    github_url = os.getenv('GITHUB_BACKUP_URL', 'https://api.github.com/repos/simonkey1/crud_noli/releases')
    
    if not github_token:
        logger.warning("GITHUB_TOKEN no configurado, intentando descarga pública")
        headers = {}
    else:
        headers = {'Authorization': f'token {github_token}'}
    
    try:
        logger.info("Obteniendo lista de releases desde GitHub...")
        response = requests.get(github_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        releases = response.json()
        if not releases:
            logger.error("No se encontraron releases en GitHub")
            return None
        
        # Buscar el release más reciente que tenga archivos .zip
        for release in releases:
            assets = release.get('assets', [])
            zip_assets = [asset for asset in assets if asset['name'].endswith('.zip')]
            
            if zip_assets:
                asset = zip_assets[0]  # Tomar el primer .zip encontrado
                logger.info(f"Descargando backup: {asset['name']}")
                
                # Descargar el archivo
                download_response = requests.get(asset['browser_download_url'], headers=headers, timeout=300)
                download_response.raise_for_status()
                
                # Guardar el archivo
                backup_dir = Path(__file__).parent.parent / 'backups'
                backup_dir.mkdir(exist_ok=True)
                backup_file = backup_dir / asset['name']
                
                with open(backup_file, 'wb') as f:
                    f.write(download_response.content)
                
                logger.info(f"Backup descargado: {backup_file}")
                return str(backup_file)
        
        logger.error("No se encontraron archivos .zip en los releases de GitHub")
        return None
        
    except Exception as e:
        logger.error(f"Error descargando backup desde GitHub: {e}")
        return None

def restore_robust_backup(backup_file):
    """
    Usa la lógica de restauración robusta con mapeo de IDs
    Basado en tools/restore_with_reset.py
    """
    from models.user import User
    from models.order import CierreCaja, OrdenItem
    
    logger.info(f"Iniciando restauración robusta desde: {backup_file}")
    
    # Mapeos para convertir IDs antiguos a nuevos
    categoria_id_map = {}
    producto_id_map = {}
    cierre_id_map = {}
    orden_id_map = {}
    
    try:
        with zipfile.ZipFile(backup_file, 'r') as backup_zip:
            with Session(engine) as session:
                
                # 1. Restaurar categorías
                logger.info("Restaurando categorías...")
                with backup_zip.open('categorias.json') as f:
                    categorias = json.load(f)
                
                for cat_data in categorias:
                    old_id = cat_data['id']
                    cat_data_copy = {k: v for k, v in cat_data.items() if k != 'id'}
                    
                    categoria = Categoria(**cat_data_copy)
                    session.add(categoria)
                    session.flush()
                    categoria_id_map[old_id] = categoria.id
                
                session.commit()
                logger.info(f"✅ {len(categorias)} categorías restauradas")
                
                # 2. Restaurar productos
                logger.info("Restaurando productos...")
                with backup_zip.open('productos.json') as f:
                    productos = json.load(f)
                
                for prod_data in productos:
                    old_id = prod_data['id']
                    old_categoria_id = prod_data.get('categoria_id')
                    
                    if old_categoria_id and old_categoria_id in categoria_id_map:
                        prod_data['categoria_id'] = categoria_id_map[old_categoria_id]
                    
                    prod_data_copy = {k: v for k, v in prod_data.items() if k != 'id'}
                    
                    producto = Producto(**prod_data_copy)
                    session.add(producto)
                    session.flush()
                    producto_id_map[old_id] = producto.id
                
                session.commit()
                logger.info(f"✅ {len(productos)} productos restaurados")
                
                # 3. Restaurar cierres de caja
                logger.info("Restaurando cierres de caja...")
                with backup_zip.open('cierres_caja.json') as f:
                    cierres = json.load(f)
                
                for cierre_data in cierres:
                    old_id = cierre_data['id']
                    cierre_data_copy = {k: v for k, v in cierre_data.items() if k != 'id'}
                    
                    cierre = CierreCaja(**cierre_data_copy)
                    session.add(cierre)
                    session.flush()
                    cierre_id_map[old_id] = cierre.id
                
                session.commit()
                logger.info(f"✅ {len(cierres)} cierres de caja restaurados")
                
                # 4. Restaurar órdenes/transacciones
                logger.info("Restaurando transacciones...")
                with backup_zip.open('transacciones.json') as f:
                    transacciones = json.load(f)
                
                for trans_data in transacciones:
                    old_id = trans_data['id']
                    old_cierre_id = trans_data.get('cierre_id')
                    
                    if old_cierre_id and old_cierre_id in cierre_id_map:
                        trans_data['cierre_id'] = cierre_id_map[old_cierre_id]
                    
                    trans_data_copy = {k: v for k, v in trans_data.items() if k != 'id'}
                    
                    orden = Orden(**trans_data_copy)
                    session.add(orden)
                    session.flush()
                    orden_id_map[old_id] = orden.id
                
                session.commit()
                logger.info(f"✅ {len(transacciones)} transacciones restauradas")
                
                # 5. Restaurar items de transacciones
                logger.info("Restaurando items de transacciones...")
                with backup_zip.open('transaccion_items.json') as f:
                    items = json.load(f)
                
                items_exitosos = 0
                items_omitidos = 0
                
                for item_data in items:
                    old_orden_id = item_data.get('orden_id')
                    old_producto_id = item_data.get('producto_id')
                    
                    if old_orden_id not in orden_id_map:
                        logger.warning(f"Omitiendo item: orden_id {old_orden_id} no encontrada")
                        items_omitidos += 1
                        continue
                        
                    if old_producto_id not in producto_id_map:
                        logger.warning(f"Omitiendo item: producto_id {old_producto_id} no encontrado")
                        items_omitidos += 1
                        continue
                    
                    item_data['orden_id'] = orden_id_map[old_orden_id]
                    item_data['producto_id'] = producto_id_map[old_producto_id]
                    
                    item_data_copy = {k: v for k, v in item_data.items() if k != 'id'}
                    
                    item = OrdenItem(**item_data_copy)
                    session.add(item)
                    items_exitosos += 1
                
                session.commit()
                logger.info(f"✅ {items_exitosos} items restaurados, {items_omitidos} omitidos")
                
                # 6. Restaurar usuarios
                logger.info("Restaurando usuarios...")
                try:
                    with backup_zip.open('usuarios.json') as f:
                        usuarios = json.load(f)
                    
                    for user_data in usuarios:
                        user_data_copy = {k: v for k, v in user_data.items() if k not in ['id', 'email']}
                        
                        username = user_data_copy.get('username', '')
                        existing_user = session.exec(select(User).where(User.username == username)).first()
                        
                        if not existing_user:
                            user = User(**user_data_copy)
                            session.add(user)
                    
                    session.commit()
                    logger.info(f"✅ {len(usuarios)} usuarios procesados")
                    
                except Exception as e:
                    logger.warning(f"Error restaurando usuarios: {e}")
        
        logger.info("🎉 Restauración robusta completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"Error durante la restauración robusta: {e}")
        return False

def main():
    """Función principal de post-deploy"""
    logger.info("🚀 Iniciando post-deploy script")
    
    # Verificar si debemos ejecutar la restauración
    post_deploy_restore = os.getenv('POST_DEPLOY_RESTORE', 'false').lower() == 'true'
    auto_restore_empty = os.getenv('AUTO_RESTORE_ON_EMPTY', 'true').lower() == 'true'
    force_restore = os.getenv('POST_DEPLOY_FORCE', 'false').lower() == 'true'
    
    logger.info(f"Configuración:")
    logger.info(f"  POST_DEPLOY_RESTORE: {post_deploy_restore}")
    logger.info(f"  AUTO_RESTORE_ON_EMPTY: {auto_restore_empty}")
    logger.info(f"  POST_DEPLOY_FORCE: {force_restore}")
    
    # Verificar estado de la base de datos
    is_empty = check_database_empty()
    
    should_restore = force_restore or (post_deploy_restore and (auto_restore_empty and is_empty))
    
    if not should_restore:
        logger.info("No se requiere restauración de datos")
        return True
    
    logger.info("Iniciando proceso de restauración...")
    
    # Intentar descargar backup desde GitHub
    backup_file = download_github_backup()
    
    if not backup_file:
        logger.error("No se pudo obtener el backup desde GitHub")
        return False
    
    # Ejecutar restauración robusta
    success = restore_robust_backup(backup_file)
    
    if success:
        logger.info("✅ Post-deploy completado exitosamente")
    else:
        logger.error("❌ Error durante el post-deploy")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
