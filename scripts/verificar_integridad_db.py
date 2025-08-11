#!/usr/bin/env python
# Script para verificar la integridad de la base de datos

import sys
import os

# Agregar el directorio raíz al path para importar desde los módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import engine
from sqlmodel import Session
from sqlalchemy import text
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verificar_integridad():
    """Verifica la integridad de la base de datos"""
    with Session(engine) as session:
        # 1. Verificar si hay duplicados en las tablas principales
        print("\n===== VERIFICACIÓN DE INTEGRIDAD DE LA BASE DE DATOS =====")
        print("\n=== DUPLICADOS EN TABLAS PRINCIPALES ===")
        
        # Verificar duplicados en productos por nombre
        print("\n=== Verificando duplicados en tabla producto ===")
        query = text("""
            SELECT nombre, COUNT(*) as num_duplicados, array_agg(id) as ids
            FROM producto
            GROUP BY nombre
            HAVING COUNT(*) > 1
        """)
        
        result = session.execute(query).fetchall()
        if result:
            print(f"Se encontraron {len(result)} nombres de productos duplicados:")
            for row in result:
                nombre, count, ids = row
                print(f"  Nombre: '{nombre}' - {count} duplicados - IDs: {ids}")
        else:
            print("No hay nombres de productos duplicados.")
            
        # Verificar duplicados en categorías
        print("\n=== Verificando duplicados en tabla categoria ===")
        query = text("""
            SELECT id, COUNT(*) as num_duplicados
            FROM categoria
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        
        result = session.execute(query).fetchall()
        if result:
            print(f"ALERTA: Se encontraron {len(result)} IDs duplicados en categoria")
        else:
            print("No hay IDs duplicados en categoria.")
            
        # Verificar duplicados en órdenes
        print("\n=== Verificando duplicados en tabla orden ===")
        query = text("""
            SELECT id, COUNT(*) as num_duplicados
            FROM orden
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        
        result = session.execute(query).fetchall()
        if result:
            print(f"ALERTA: Se encontraron {len(result)} IDs duplicados en orden")
        else:
            print("No hay IDs duplicados en orden.")
        
        # Verificar duplicados en ordenitem
        print("\n=== Verificando duplicados en tabla ordenitem ===")
        query = text("""
            SELECT id, COUNT(*) as num_duplicados
            FROM ordenitem
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        
        result = session.execute(query).fetchall()
        if result:
            print(f"ALERTA: Se encontraron {len(result)} IDs duplicados en ordenitem")
        else:
            print("No hay IDs duplicados en ordenitem.")
            
        # Verificar duplicados en cierrecaja
        print("\n=== Verificando duplicados en tabla cierrecaja ===")
        query = text("""
            SELECT id, COUNT(*) as num_duplicados
            FROM cierrecaja
            GROUP BY id
            HAVING COUNT(*) > 1
        """)
        
        result = session.execute(query).fetchall()
        if result:
            print(f"ALERTA: Se encontraron {len(result)} IDs duplicados en cierrecaja")
        else:
            print("No hay IDs duplicados en cierrecaja.")

        # 2. Verificar referencias huérfanas
        print("\n=== REFERENCIAS HUÉRFANAS ===")
        
        # Verificar items que referencian a órdenes inexistentes
        query = text("""
            SELECT COUNT(*) FROM ordenitem oi
            WHERE NOT EXISTS (SELECT 1 FROM orden o WHERE o.id = oi.orden_id)
        """)
        result = session.execute(query).scalar()
        print(f"Items huérfanos (sin orden): {result}")
        
        # Verificar items que referencian a productos inexistentes
        query = text("""
            SELECT COUNT(*) FROM ordenitem oi
            WHERE NOT EXISTS (SELECT 1 FROM producto p WHERE p.id = oi.producto_id)
        """)
        result = session.execute(query).scalar()
        print(f"Items huérfanos (sin producto): {result}")
        
        # Verificar productos que referencian a categorías inexistentes
        query = text("""
            SELECT COUNT(*) FROM producto p
            WHERE p.categoria_id IS NOT NULL 
            AND NOT EXISTS (SELECT 1 FROM categoria c WHERE c.id = p.categoria_id)
        """)
        result = session.execute(query).scalar()
        print(f"Productos huérfanos (sin categoría): {result}")
        
        # 3. Resumen estadístico
        print("\n=== RESUMEN ESTADÍSTICO DE LA BASE DE DATOS ===")
        
        # Contar registros en cada tabla
        tablas = ["producto", "categoria", "orden", "ordenitem", "cierrecaja"]
        for tabla in tablas:
            query = text(f"SELECT COUNT(*) FROM {tabla}")
            count = session.execute(query).scalar()
            print(f"Total de registros en {tabla}: {count}")
        
        try:
            # Intentar contar usuarios sin asumir estructura
            query = text(f"SELECT COUNT(*) FROM \"user\"")
            count = session.execute(query).scalar()
            print(f"Total de usuarios: {count}")
        except Exception as e:
            print(f"No se pudo contar usuarios: {str(e)}")

def examinar_duplicados_producto():
    """Examina en detalle los productos duplicados y proporciona información para resolverlo"""
    with Session(engine) as session:
        query = text("""
            SELECT 
                p1.id as id1, p1.nombre as nombre1, p1.precio as precio1, p1.categoria_id as cat1,
                p2.id as id2, p2.nombre as nombre2, p2.precio as precio2, p2.categoria_id as cat2
            FROM producto p1
            JOIN producto p2 ON LOWER(p1.nombre) = LOWER(p2.nombre) AND p1.id < p2.id
            ORDER BY LOWER(p1.nombre)
        """)
        duplicados = session.execute(query).fetchall()
        
        if not duplicados:
            print("No se encontraron productos duplicados para examinar.")
            return
            
        print(f"\n=== DETALLE DE {len(duplicados)} PRODUCTOS DUPLICADOS ===")
        for dup in duplicados:
            print(f"Producto 1: ID={dup.id1}, Nombre='{dup.nombre1}', Precio={dup.precio1}, CategoriaID={dup.cat1}")
            print(f"Producto 2: ID={dup.id2}, Nombre='{dup.nombre2}', Precio={dup.precio2}, CategoriaID={dup.cat2}")
            
            # Verificar si alguno de estos productos tiene órdenes asociadas
            query_ordenes = text(f"""
                SELECT 
                    (SELECT COUNT(*) FROM ordenitem WHERE producto_id = {dup.id1}) as count1,
                    (SELECT COUNT(*) FROM ordenitem WHERE producto_id = {dup.id2}) as count2
            """)
            counts = session.execute(query_ordenes).fetchone()
            
            print(f"Órdenes asociadas: Producto 1: {counts[0]}, Producto 2: {counts[1]}")
            print("-" * 50)

def examinar_cierres_caja():
    """Examina en detalle los cierres de caja y muestra información relevante"""
    with Session(engine) as session:
        # Primero obtengamos las columnas reales de la tabla
        try:
            query_columns = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'cierrecaja'
                ORDER BY ordinal_position
            """)
            columnas = [row[0] for row in session.execute(query_columns).fetchall()]
            print(f"Columnas en tabla cierrecaja: {columnas}")
            
            # Construir consulta dinámica con las columnas disponibles
            columnas_sql = ", ".join(columnas)
            query = text(f"""
                SELECT {columnas_sql}
                FROM cierrecaja
                ORDER BY id
            """)
            
            cierres = session.execute(query).fetchall()
            
            if not cierres:
                print("No se encontraron cierres de caja.")
                return
                
            print(f"\n=== DETALLE DE {len(cierres)} CIERRES DE CAJA ===")
            
            for cierre in cierres:
                print(f"ID: {cierre.id}")
                
                # Mostrar fecha y fecha_cierre si están disponibles
                if 'fecha' in columnas:
                    print(f"Fecha apertura: {cierre.fecha}")
                if 'fecha_cierre' in columnas:
                    print(f"Fecha cierre: {cierre.fecha_cierre}")
                
                # Mostrar totales financieros
                if 'total_ventas' in columnas:
                    print(f"Total ventas: ${cierre.total_ventas}")
                if 'total_efectivo' in columnas:
                    print(f"Total efectivo: ${cierre.total_efectivo}")
                if 'total_debito' in columnas:
                    print(f"Total débito: ${cierre.total_debito}")
                if 'total_credito' in columnas:
                    print(f"Total crédito: ${cierre.total_credito}")
                if 'total_transferencia' in columnas:
                    print(f"Total transferencia: ${cierre.total_transferencia}")
                    
                # Información de ganancias
                if 'total_costo' in columnas:
                    print(f"Total costo: ${cierre.total_costo}")
                if 'total_ganancia' in columnas:
                    print(f"Total ganancia: ${cierre.total_ganancia}")
                if 'margen_promedio' in columnas:
                    print(f"Margen promedio: {cierre.margen_promedio}%")
                
                # Información de transacciones
                if 'cantidad_transacciones' in columnas:
                    print(f"Cantidad transacciones: {cierre.cantidad_transacciones}")
                if 'ticket_promedio' in columnas:
                    print(f"Ticket promedio: ${cierre.ticket_promedio}")
                
                # Usuario
                if 'usuario_nombre' in columnas and cierre.usuario_nombre:
                    print(f"Usuario: {cierre.usuario_nombre}")
                
                # Verificar si hay transacciones asociadas a este cierre
                query_transacciones = text(f"""
                    SELECT COUNT(*) FROM orden
                    WHERE cierre_id = {cierre.id}
                """)
                
                try:
                    count = session.execute(query_transacciones).scalar() or 0
                    print(f"Transacciones asociadas: {count}")
                except Exception as e:
                    print(f"No se pudo verificar transacciones asociadas: {str(e)}")
                    
                print("-" * 50)
                
        except Exception as e:
            print(f"Error al examinar cierres de caja: {str(e)}")

def verificar_secuencias_tablas():
    """Verifica que las secuencias de las tablas estén sincronizadas con los IDs máximos"""
    with Session(engine) as session:
        tablas = ["producto", "categoria", "orden", "ordenitem", "cierrecaja"]
        print("\n=== VERIFICACIÓN DE SECUENCIAS ===")
        
        for tabla in tablas:
            # Obtener el ID máximo de la tabla
            query_max = text(f"SELECT MAX(id) FROM {tabla}")
            max_id = session.execute(query_max).scalar() or 0
            
            # Obtener el valor actual de la secuencia
            query_seq = text(f"SELECT COALESCE(last_value, 0) FROM {tabla}_id_seq")
            try:
                seq_value = session.execute(query_seq).scalar() or 0
                
                if max_id > seq_value:
                    print(f"ALERTA: La secuencia de {tabla} ({seq_value}) está por detrás del ID máximo ({max_id})")
                else:
                    print(f"Secuencia de {tabla} correcta: valor actual = {seq_value}, ID máximo = {max_id}")
            except Exception as e:
                print(f"Error al verificar secuencia de {tabla}: {str(e)}")

if __name__ == "__main__":
    verificar_integridad()
    print("\n" + "=" * 60)
    examinar_duplicados_producto()
    print("\n" + "=" * 60)
    examinar_cierres_caja()
    print("\n" + "=" * 60)
    verificar_secuencias_tablas()
