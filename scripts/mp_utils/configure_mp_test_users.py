# Script para actualizar la configuración de Mercado Pago con los usuarios de prueba
import os
import json
from pathlib import Path

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Cargar los datos de los usuarios de prueba
mp_test_users_path = os.path.join(current_dir, 'mp_test_users.json')
with open(mp_test_users_path, 'r') as f:
    test_users = json.load(f)

# Obtener los datos del comprador
buyer_email = test_users['buyer']['email']

# Imprimir la información
print("=== Información de los usuarios de prueba ===")
print(f"Vendedor: {test_users['seller']['email']}")
print(f"Comprador: {buyer_email}")
print("\n")
print("Para configurar Mercado Pago correctamente:")
print("1. Actualiza tu archivo .env con las siguientes variables:")
print("   - MERCADO_PAGO_ACCESS_TOKEN: [Tu ACCESS TOKEN del vendedor]")
print("   - MERCADO_PAGO_PUBLIC_KEY: [Tu PUBLIC KEY del vendedor]")
print(f"   - MERCADO_PAGO_TEST_USER_EMAIL: {buyer_email}")
print("\n2. O modifica directamente el archivo core/config.py:")
print(f"   - Reemplaza MERCADO_PAGO_TEST_USER_EMAIL: '{buyer_email}'")
print("   - Actualiza MERCADO_PAGO_ACCESS_TOKEN y MERCADO_PAGO_PUBLIC_KEY con tus credenciales")

# Actualizar directamente config.py
config_path = os.path.join(current_dir, 'core', 'config.py')

if os.path.exists(config_path):
    # Leer el archivo de configuración
    with open(config_path, 'r') as f:
        config_content = f.read()
    
    # Actualizar la configuración del email del comprador
    # Buscar la línea que contiene MERCADO_PAGO_TEST_USER_EMAIL
    import re
    pattern = r'(MERCADO_PAGO_TEST_USER_EMAIL:\s*str\s*=\s*Field\(\")([^\"]+)(\",\s*env=\"MERCADO_PAGO_TEST_USER_EMAIL\"\))'
    replacement = f'\\1{buyer_email}\\3'
    
    new_config = re.sub(pattern, replacement, config_content)
    
    # Guardar el archivo actualizado
    with open(config_path, 'w') as f:
        f.write(new_config)
    
    print("\n✅ Se ha actualizado automáticamente el email del usuario de prueba en core/config.py")
    print("⚠️ Recuerda actualizar manualmente el ACCESS_TOKEN y PUBLIC_KEY si es necesario")
else:
    print("\n⚠️ No se encontró el archivo core/config.py")
    print("   Debes actualizar manualmente la configuración")

print("\n🔄 Recuerda reiniciar la aplicación después de actualizar la configuración")
