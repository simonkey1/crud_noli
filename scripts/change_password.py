#!/usr/bin/env python
# scripts/change_password.py

import sys
import os
import getpass
import time

# Agregar el directorio raíz al path para poder importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from db.database import engine
from models.user import User
from utils.security import hash_password, verify_password

def change_password(username, new_password, skip_verification=False):
    """Cambia la contraseña de un usuario existente"""
    with Session(engine) as session:
        # Buscar el usuario
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"Error: El usuario '{username}' no existe.")
            return False
        
        # Verificar la contraseña actual si no se omite la verificación
        if not skip_verification:
            current_password = getpass.getpass("Introduce la contraseña actual: ")
            if not verify_password(current_password, user.hashed_password):
                print("Contraseña incorrecta. No se puede cambiar la contraseña.")
                time.sleep(2)  # Pequeña pausa para prevenir ataques de fuerza bruta
                return False
        
        # Actualizar la contraseña
        user.hashed_password = hash_password(new_password)
        session.add(user)
        session.commit()
        print(f"Contraseña cambiada exitosamente para el usuario '{username}'.")
        return True

if __name__ == "__main__":
    print("=== Cambio de contraseña ===")
    
    # Verificar si el usuario es administrador
    is_admin = False
    admin_override = False
    
    # Solicitar nombre de usuario
    username = input("Introduce el nombre de usuario: ").strip()
    if not username:
        print("Error: Debes introducir un nombre de usuario.")
        sys.exit(1)
    
    # Verificar si se está cambiando la contraseña del administrador
    if username == "admin":
        print("¡Atención! Estás cambiando la contraseña del administrador.")
        print("Para mayor seguridad, usa el script reset_admin.py para esta operación.")
        confirm = input("¿Quieres continuar de todos modos? (s/n): ").lower()
        if confirm != 's':
            sys.exit(0)
    
    # Si el usuario actual es administrador, ofrecer opción de omitir verificación
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if admin:
            admin_auth = input("¿Eres el administrador del sistema? (s/n): ").lower()
            if admin_auth == 's':
                admin_password = getpass.getpass("Introduce la contraseña de administrador para verificar: ")
                if verify_password(admin_password, admin.hashed_password):
                    is_admin = True
                    if username != "admin":  # No permitir cambio de admin sin verificación adecuada
                        admin_override = input("¿Quieres cambiar la contraseña sin verificación previa? (s/n): ").lower() == 's'
                else:
                    print("Verificación de administrador fallida.")
    
    # Solicitar y validar la nueva contraseña
    while True:
        new_password = getpass.getpass("Introduce la nueva contraseña (mínimo 8 caracteres): ")
        if len(new_password) < 8:
            print("La contraseña debe tener al menos 8 caracteres.")
            continue
            
        confirm_password = getpass.getpass("Confirma la contraseña: ")
        if new_password != confirm_password:
            print("Las contraseñas no coinciden. Inténtalo de nuevo.")
            continue
        
        # Cambiar la contraseña
        if change_password(username, new_password, skip_verification=admin_override):
            print("\nRecuerda usar esta nueva contraseña la próxima vez que inicies sesión.")
        break
