# Script para actualizar la configuración de Mercado Pago con Vendedor_2 y Comprador_2
# Ejecuta este script con: python actualizar_vendedor_comprador.py

import json
import os

# Ruta del archivo de configuración de Mercado Pago nuevo
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'mp_test_users_nuevos.json')

# Función para cargar usuarios de prueba
def load_test_users():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def main():
    # Cargar usuarios de prueba
    users = load_test_users()
    
    # Información del vendedor
    seller = users.get('seller', {})
    seller_email = seller.get('email', '')
    seller_password = seller.get('password', '')
    
    # Información del comprador
    buyer = users.get('buyer', {})
    buyer_email = buyer.get('email', '')
    buyer_password = buyer.get('password', '')
    
    print("=== Configuración de Mercado Pago - Vendedor_2 y Comprador_2 ===")
    print(f"Usuario vendedor: {seller_email}")
    print(f"Usuario comprador: {buyer_email}")
    print("\n")
    
    # Solicitar ACCESS TOKEN del vendedor
    print("Para completar la configuración, necesitas el ACCESS TOKEN del Vendedor_2.")
    print("Puedes obtenerlo en: https://www.mercadopago.com.cl/developers/panel/credentials")
    print("Inicia sesión con el email del vendedor (Vendedor_2).")
    
    access_token = input("Ingresa el ACCESS TOKEN del Vendedor_2: ")
    public_key = input("Ingresa el PUBLIC KEY del Vendedor_2: ")
    
    # Crear o actualizar archivo .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # Verificar si ya existe el archivo .env
    env_exists = os.path.exists(env_path)
    env_content = ""
    
    if env_exists:
        with open(env_path, 'r') as f:
            env_content = f.read()
    
    # Actualizar o agregar las variables de entorno
    env_lines = env_content.split('\n')
    updated_env = []
    
    # Variables a actualizar
    env_vars = {
        'MERCADO_PAGO_ACCESS_TOKEN': access_token,
        'MERCADO_PAGO_PUBLIC_KEY': public_key,
        'MERCADO_PAGO_TEST_USER_EMAIL': buyer_email,
        'MERCADO_PAGO_TEST_USER_PASSWORD': buyer_password,
        'MERCADO_PAGO_TEST_SELLER_EMAIL': seller_email,
        'MERCADO_PAGO_TEST_SELLER_PASSWORD': seller_password
    }
    
    # Mantener variables existentes y actualizar las de Mercado Pago
    updated_vars = set()
    for line in env_lines:
        if line.strip() and '=' in line:
            key = line.split('=')[0].strip()
            if key in env_vars:
                updated_env.append(f"{key}={env_vars[key]}")
                updated_vars.add(key)
            else:
                updated_env.append(line)
    
    # Agregar variables que no existían
    for key, value in env_vars.items():
        if key not in updated_vars:
            updated_env.append(f"{key}={value}")
    
    # Guardar el archivo .env actualizado
    with open(env_path, 'w') as f:
        f.write('\n'.join(updated_env))
    
    # Actualizar también el archivo mp_test_users.json
    with open(os.path.join(os.path.dirname(__file__), 'mp_test_users.json'), 'w') as f:
        json.dump(users, f, indent=4)
    
    print("\n=== Configuración actualizada ===")
    print(f"Se han actualizado las siguientes variables en el archivo .env:")
    for key, value in env_vars.items():
        masked_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '****'
        print(f"{key}={masked_value}")
    
    print("\nRecuerda reiniciar la aplicación para que los cambios surtan efecto.")
    print("También se ha actualizado el archivo mp_test_users.json con los nuevos usuarios.")

if __name__ == "__main__":
    main()
