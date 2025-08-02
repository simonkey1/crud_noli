#!/usr/bin/env python
"""
Script para habilitar Row Level Security (RLS) en tablas de Supabase.
Ejecutar con: python -m scripts.enable_rls
"""

import os
from sqlmodel import Session, text
from db.database import engine
from core.config import settings
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def enable_rls():
    """Habilita Row Level Security en tablas públicas y define políticas básicas"""
    
    logger.info(f"Conectando a la base de datos: {settings.POSTGRES_SERVER}")
    
    with Session(engine) as session:
        try:
            # Primero, verificamos la estructura de la tabla usuario para determinar el tipo de ID
            try:
                result = session.execute(text("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'user' AND column_name = 'id'
                """)).scalar()
                
                logger.info(f"Tipo de dato para la columna 'id' en la tabla 'user': {result}")
                
                # Determinar la función de conversión apropiada basada en el tipo de columna
                if result and result.lower() == 'integer':
                    # Si el id es integer, necesitamos una forma segura de manejar la conversión
                    # Evitamos conversiones directas que puedan fallar
                    auth_uid_cast = "(auth.uid())::text"
                    id_comparison = "id::text"
                    logger.info("Se usará comparación de texto para auth.uid() y id")
                else:
                    # Si es UUID o cualquier otro tipo, usamos auth.uid() sin conversión
                    auth_uid_cast = "auth.uid()"
                    id_comparison = "id::text"
                    logger.info("Se usará auth.uid() con comparación de texto")
            except Exception as e:
                # Si hay un error al verificar, usamos una conversión segura por defecto
                logger.warning(f"No se pudo determinar el tipo de id: {str(e)}. Usando conversión por defecto.")
                auth_uid_cast = "(auth.uid())::text"
                id_comparison = "id::text"
            
            # Lista de tablas a las que aplicar RLS
            tables = [
                "categoria", 
                "producto", 
                "orden", 
                "ordenitem", 
                "user", 
                # No incluimos alembic_version ya que es una tabla de sistema
            ]
            
            # Habilitamos RLS en cada tabla
            for table in tables:
                logger.info(f"Habilitando RLS para tabla: {table}")
                
                # 1. Habilitar RLS en la tabla
                session.execute(text(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY;'))
                
                # 2. Eliminar políticas existentes (si las hay)
                session.execute(text(f'DROP POLICY IF EXISTS "Política autenticada {table}" ON public."{table}";'))
                session.execute(text(f'DROP POLICY IF EXISTS "Política admin {table}" ON public."{table}";'))
                session.execute(text(f'DROP POLICY IF EXISTS "Política lectura {table}" ON public."{table}";'))
                session.execute(text(f'DROP POLICY IF EXISTS "Política escritura {table}" ON public."{table}";'))
                session.execute(text(f'DROP POLICY IF EXISTS "Política usuario {table}" ON public."{table}";'))
                
                # 3. Crear políticas adecuadas según el tipo de tabla
                
                # Para users: solo administradores pueden ver todos, usuarios normales solo su propio registro
                if table == "user":
                    session.execute(text(f'''
                        CREATE POLICY "Política autenticada user" 
                        ON public."user"
                        FOR ALL
                        TO authenticated
                        USING (id::text = {auth_uid_cast}::text OR 
                              (SELECT is_superuser FROM public."user" WHERE id::text = {auth_uid_cast}::text));
                    '''))
                    
                # Para productos y categorías: todos pueden ver, solo admins pueden modificar
                elif table in ["categoria", "producto"]:
                    # Política para lectura: todos pueden leer
                    session.execute(text(f'''
                        CREATE POLICY "Política lectura {table}" 
                        ON public."{table}"
                        FOR SELECT
                        TO authenticated
                        USING (TRUE);
                    '''))
                    
                    # Política para escritura: solo admins
                    session.execute(text(f'''
                        CREATE POLICY "Política escritura {table}" 
                        ON public."{table}"
                        FOR ALL
                        TO authenticated
                        USING (EXISTS (
                            SELECT 1 FROM public."user" 
                            WHERE {id_comparison} = {auth_uid_cast}
                            AND is_superuser = TRUE
                        ));
                    '''))
                
                # Para órdenes y items de órdenes: usuarios ven sus propias órdenes, admins ven todas
                elif table in ["orden", "ordenitem"]:
                    # Admins ven y modifican todo
                    session.execute(text(f'''
                        CREATE POLICY "Política admin {table}" 
                        ON public."{table}"
                        FOR ALL
                        TO authenticated
                        USING (EXISTS (
                            SELECT 1 FROM public."user" 
                            WHERE {id_comparison} = {auth_uid_cast}
                            AND is_superuser = TRUE
                        ));
                    '''))
                    
                    if table == "orden":
                        # Para la tabla orden, por ahora permitimos acceso a todos los usuarios autenticados
                        # Ya que no hay campo usuario_id
                        session.execute(text(f'''
                            CREATE POLICY "Política usuario {table}" 
                            ON public."{table}"
                            FOR ALL
                            TO authenticated
                            USING (TRUE);
                        '''))
                    else:  # ordenitem
                        # Para orden_items, por ahora permitimos acceso a todos los usuarios autenticados
                        # Ya que no podemos vincular con usuario_id
                        session.execute(text(f'''
                            CREATE POLICY "Política usuario {table}" 
                            ON public."{table}"
                            FOR ALL
                            TO authenticated
                            USING (TRUE);
                        '''))
            
            session.commit()
            logger.info("RLS habilitado exitosamente en todas las tablas")
            
        except Exception as e:
            logger.error(f"Error al habilitar RLS: {str(e)}")
            session.rollback()
            raise

if __name__ == "__main__":
    enable_rls()
