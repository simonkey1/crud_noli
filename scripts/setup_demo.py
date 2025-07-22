# scripts/setup_demo.py

"""
Script para configurar una demo completa:
1. Crear las categorías
2. Cargar productos de ejemplo
"""

from scripts.create_categories import create_categories
from scripts.seed_sample_products import seed_sample_products

def setup_demo():
    print("1. Creando categorías...")
    create_categories()
    
    print("\n2. Cargando productos de ejemplo...")
    seed_sample_products()
    
    print("\n✅ Demo configurada correctamente!")

if __name__ == "__main__":
    setup_demo()
