#!/usr/bin/env python
"""
Script para verificar el estado de seguridad de Supabase
Este script se conecta a la base de datos y verifica el estado de seguridad
"""
import os
import sys
import argparse
from sqlalchemy import create_engine, text
from tabulate import tabulate

# Agregar el directorio raíz al path para importar desde los módulos
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(root_dir)

from core.config import settings

def check_security_status():
    """Verifica el estado de seguridad en la base de datos Supabase"""
    
    # Conectar a la base de datos
    print(f"🔄 Conectando a la base de datos: {settings.DATABASE_URL}")
    try:
        engine = create_engine(settings.DATABASE_URL, echo=False)
        connection = engine.connect()
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {str(e)}")
        return False
    
    try:
        # 1. Verificar RLS en las tablas
        print("\n🔍 Verificando Row Level Security en tablas...")
        rls_query = text("""
            SELECT tablename, rowsecurity
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        rls_result = connection.execute(rls_query).fetchall()
        rls_data = [[r[0], "✅ Habilitado" if r[1] else "❌ Deshabilitado"] for r in rls_result]
        print(tabulate(rls_data, headers=["Tabla", "RLS Status"], tablefmt="grid"))
        
        # 2. Verificar políticas RLS
        print("\n🔍 Verificando políticas RLS...")
        policy_query = text("""
            SELECT tablename, policyname, permissive, cmd, qual, with_check
            FROM pg_policies
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname
        """)
        policy_result = connection.execute(policy_query).fetchall()
        policy_data = [[r[0], r[1], r[3], "Permisiva" if r[2] else "Restrictiva"] for r in policy_result]
        print(tabulate(policy_data, headers=["Tabla", "Política", "Operación", "Tipo"], tablefmt="grid"))
        
        # 3. Verificar índices
        print("\n🔍 Verificando índices en claves foráneas...")
        index_query = text("""
            SELECT
                tc.table_name, 
                kcu.column_name,
                CASE WHEN i.indexname IS NOT NULL THEN '✅ Presente' ELSE '❌ Faltante' END as index_status
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                LEFT JOIN pg_indexes i
                  ON i.tablename = tc.table_name 
                  AND i.indexdef LIKE '%' || kcu.column_name || '%'
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_schema = 'public'
            ORDER BY 
                tc.table_name, 
                kcu.column_name;
        """)
        index_result = connection.execute(index_query).fetchall()
        index_data = [[r[0], r[1], r[2]] for r in index_result]
        print(tabulate(index_data, headers=["Tabla", "Columna FK", "Estado Índice"], tablefmt="grid"))
        
        # 4. Verificar funciones y sus permisos
        print("\n🔍 Verificando permisos de funciones...")
        function_query = text("""
            SELECT
                n.nspname as schema,
                p.proname as function_name,
                CASE p.prosecdef WHEN true THEN 'SECURITY DEFINER' ELSE 'SECURITY INVOKER' END as security_type,
                pg_catalog.pg_get_userbyid(p.proowner) as owner
            FROM
                pg_catalog.pg_proc p
                LEFT JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
            WHERE
                n.nspname = 'public'
            ORDER BY
                schema, function_name;
        """)
        function_result = connection.execute(function_query).fetchall()
        function_data = [[r[1], r[2], r[3]] for r in function_result]
        print(tabulate(function_data, headers=["Función", "Tipo Seguridad", "Propietario"], tablefmt="grid"))
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar seguridad: {str(e)}")
        connection.close()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verifica el estado de seguridad en Supabase")
    args = parser.parse_args()
    
    if check_security_status():
        sys.exit(0)
    else:
        sys.exit(1)
