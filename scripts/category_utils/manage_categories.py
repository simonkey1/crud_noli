# scripts/manage_categories.py

from sqlmodel import Session, select
from db.database import engine
from models.models import Categoria

def confirmar_accion(mensaje="¿Desea continuar con la operación?"):
    """Solicita confirmación al usuario para continuar con una operación"""
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta in ('s', 'si', 'sí', 'y', 'yes')

def list_categories():
    """Lista todas las categorías existentes"""
    with Session(engine) as session:
        categorias = session.exec(select(Categoria).order_by(Categoria.nombre)).all()
        print("\nCategorías existentes:")
        for cat in categorias:
            print(f"ID: {cat.id}, Nombre: {cat.nombre}")
        print(f"Total: {len(categorias)} categorías")

def add_category(nombre):
    """Añade una nueva categoría si no existe"""
    with Session(engine) as session:
        exists = session.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
        if exists:
            print(f"La categoría '{nombre}' ya existe con ID: {exists.id}")
            return False
        
        nueva_categoria = Categoria(nombre=nombre)
        session.add(nueva_categoria)
        session.commit()
        session.refresh(nueva_categoria)
        print(f"Categoría '{nombre}' creada con ID: {nueva_categoria.id}")
        return True

def delete_category(id_or_nombre):
    """Elimina una categoría por ID o nombre"""
    with Session(engine) as session:
        # Buscar por ID si es un número
        if str(id_or_nombre).isdigit():
            categoria = session.get(Categoria, int(id_or_nombre))
        else:
            # Buscar por nombre
            categoria = session.exec(select(Categoria).where(Categoria.nombre == id_or_nombre)).first()
        
        if not categoria:
            print(f"No se encontró la categoría: {id_or_nombre}")
            return False
        
        nombre = categoria.nombre
        
        # Verificar si la categoría tiene productos asociados
        from models.models import Producto
        productos = session.exec(
            select(Producto).where(Producto.categoria_id == categoria.id)
        ).all()
        
        if productos:
            print(f"⚠️ ADVERTENCIA: La categoría '{nombre}' tiene {len(productos)} productos asociados.")
            print("Si eliminas esta categoría, estos productos quedarán sin categoría.")
            
            if not confirmar_accion("¿Desea continuar con la eliminación?"):
                print("Operación cancelada.")
                return False
        
        session.delete(categoria)
        session.commit()
        print(f"Categoría '{nombre}' eliminada")
        return True

def rename_category(id_or_nombre, nuevo_nombre):
    """Renombra una categoría existente"""
    with Session(engine) as session:
        # Buscar por ID si es un número
        if str(id_or_nombre).isdigit():
            categoria = session.get(Categoria, int(id_or_nombre))
        else:
            # Buscar por nombre
            categoria = session.exec(select(Categoria).where(Categoria.nombre == id_or_nombre)).first()
        
        if not categoria:
            print(f"No se encontró la categoría: {id_or_nombre}")
            return False
        
        viejo_nombre = categoria.nombre
        
        # Verificar si ya existe una categoría con el nuevo nombre
        existe_nombre = session.exec(
            select(Categoria).where(Categoria.nombre == nuevo_nombre)
        ).first()
        
        if existe_nombre and existe_nombre.id != categoria.id:
            print(f"⚠️ ADVERTENCIA: Ya existe una categoría con el nombre '{nuevo_nombre}'.")
            if not confirmar_accion("¿Desea continuar con el renombrado?"):
                print("Operación cancelada.")
                return False
        
        categoria.nombre = nuevo_nombre
        session.add(categoria)
        session.commit()
        print(f"Categoría renombrada: '{viejo_nombre}' → '{nuevo_nombre}'")
        return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python -m scripts.category_utils.manage_categories [listar|añadir|eliminar|renombrar] [parámetros...]")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    
    if comando == "listar":
        list_categories()
    
    elif comando == "añadir" or comando == "anadir":
        if len(sys.argv) < 3:
            print("Error: Especifica el nombre de la categoría a añadir")
            sys.exit(1)
        add_category(sys.argv[2])
    
    elif comando == "eliminar":
        if len(sys.argv) < 3:
            print("Error: Especifica el ID o nombre de la categoría a eliminar")
            sys.exit(1)
        delete_category(sys.argv[2])
    
    elif comando == "renombrar":
        if len(sys.argv) < 4:
            print("Error: Especifica el ID o nombre de la categoría y el nuevo nombre")
            sys.exit(1)
        rename_category(sys.argv[2], sys.argv[3])
    
    else:
        print(f"Comando desconocido: {comando}")
        print("Comandos disponibles: listar, añadir, eliminar, renombrar")


