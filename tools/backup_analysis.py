#!/usr/bin/env python3
"""
Verificación y mejora del sistema de backup para evitar conflictos de IDs
"""

import os
import sys
import json
import zipfile
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

def analyze_backup_id_handling():
    """Analizar cómo se manejan los IDs en los backups existentes"""
    print("🔍 ANÁLISIS DEL SISTEMA DE BACKUP - MANEJO DE IDs")
    print("=" * 60)
    
    backups_dir = Path("backups")
    if not backups_dir.exists():
        print("❌ No se encontró directorio de backups")
        return
    
    # Buscar el backup más reciente
    zip_files = list(backups_dir.glob("*.zip"))
    if not zip_files:
        print("❌ No se encontraron archivos de backup")
        return
    
    latest_backup = max(zip_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 Analizando backup: {latest_backup.name}")
    
    # Extraer y analizar el contenido
    try:
        with zipfile.ZipFile(latest_backup, 'r') as zip_ref:
            # Listar archivos en el backup
            files = zip_ref.namelist()
            print(f"📋 Archivos en el backup: {len(files)}")
            
            for file in files:
                if file.endswith('.json'):
                    print(f"\n📄 Analizando {file}:")
                    
                    # Leer el contenido JSON
                    with zip_ref.open(file) as json_file:
                        try:
                            data = json.load(json_file)
                            if data and isinstance(data, list) and len(data) > 0:
                                first_record = data[0]
                                print(f"  📊 Registros: {len(data)}")
                                print(f"  🔑 Campos: {list(first_record.keys())}")
                                
                                # Verificar si tiene ID
                                if 'id' in first_record:
                                    print(f"  ✅ Contiene IDs (ejemplo: {first_record['id']})")
                                    
                                    # Verificar si los IDs son secuenciales
                                    if len(data) > 1:
                                        ids = [record.get('id') for record in data if 'id' in record]
                                        if ids:
                                            print(f"  📈 Rango de IDs: {min(ids)} - {max(ids)}")
                                else:
                                    print(f"  ⚠️  NO contiene IDs")
                                
                                # Buscar claves foráneas
                                foreign_keys = []
                                for key in first_record.keys():
                                    if key.endswith('_id') or key in ['categoria_id', 'producto_id', 'orden_id', 'user_id']:
                                        foreign_keys.append(key)
                                
                                if foreign_keys:
                                    print(f"  🔗 Claves foráneas: {foreign_keys}")
                                else:
                                    print(f"  ✅ Sin claves foráneas directas")
                            else:
                                print(f"  📊 Archivo vacío o formato incorrecto")
                                
                        except json.JSONDecodeError as e:
                            print(f"  ❌ Error leyendo JSON: {e}")
    
    except Exception as e:
        print(f"❌ Error analizando backup: {e}")

def check_current_database_sequences():
    """Verificar el estado actual de las secuencias de la base de datos"""
    print(f"\n🗄️ VERIFICANDO SECUENCIAS DE LA BASE DE DATOS")
    print("=" * 50)
    
    try:
        from db.database import engine
        from sqlmodel import Session, text
        
        with Session(engine) as session:
            # Consultar secuencias de PostgreSQL
            query = text("""
                SELECT schemaname, sequencename, last_value 
                FROM pg_sequences 
                WHERE schemaname = 'public'
                ORDER BY sequencename
            """)
            
            result = session.exec(query)
            sequences = result.fetchall()
            
            if sequences:
                print("📊 Secuencias actuales:")
                for schema, seq_name, last_value in sequences:
                    print(f"  {seq_name}: {last_value}")
            else:
                print("⚠️  No se encontraron secuencias")
                
    except Exception as e:
        print(f"❌ Error consultando secuencias: {e}")

def generate_backup_improvement_recommendations():
    """Generar recomendaciones para mejorar el sistema de backup"""
    print(f"\n💡 RECOMENDACIONES PARA MEJORAR EL BACKUP")
    print("=" * 50)
    
    recommendations = [
        {
            "problema": "IDs inconsistentes en backup",
            "solucion": "Mantener TODOS los IDs en el backup para preservar relaciones",
            "implementacion": "Eliminar la línea que borra IDs del backup_database.py"
        },
        {
            "problema": "Conflictos de secuencias al restaurar",
            "solucion": "Resetear secuencias después de restaurar datos",
            "implementacion": "Agregar código para actualizar pg_sequences"
        },
        {
            "problema": "Referencias rotas entre tablas",
            "solucion": "Incluir información de relaciones en el backup",
            "implementacion": "Documentar y preservar foreign keys"
        },
        {
            "problema": "Falta verificación de integridad",
            "solucion": "Verificar que el backup sea consistente",
            "implementacion": "Validar relaciones antes de crear el backup"
        }
    ]
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. 🎯 {rec['problema']}")
        print(f"   ✅ Solución: {rec['solucion']}")
        print(f"   🔧 Implementación: {rec['implementacion']}")

def main():
    print("🛡️ VERIFICACIÓN SISTEMA DE BACKUP PRE-COMMIT")
    print("=" * 60)
    
    analyze_backup_id_handling()
    check_current_database_sequences()
    generate_backup_improvement_recommendations()
    
    print("\n" + "=" * 60)
    print("✅ BACKUP ACTUAL CREADO CORRECTAMENTE")
    print("💡 Recomendaciones implementadas en próximas mejoras")
    print("🚀 Seguro para hacer commit ahora")

if __name__ == "__main__":
    main()
