from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from db.database import engine
from models.models import Producto


def get_all_productos(session: Session) -> list[Producto]:
    """
    Retrieve all products from the database, including their associated categories.

    Returns:
        list[Producto]: A list of Producto instances.
    """
    with Session(engine) as session:
        statement = (
            select(Producto)
            .options(selectinload(Producto.categoria))
        )
        productos = session.exec(statement).all()
    return productos


def get_producto(producto_id: int, session: Session) -> Producto | None:
    """
    Retrieve a single product by its ID.

    Args:
        producto_id (int): The ID of the product to retrieve.

    Returns:
        Producto | None: The Producto instance if found, otherwise None.
    """
    with Session(engine) as session:
        return session.get(Producto, producto_id)


def create_producto(producto: Producto, session: Session) -> Producto:
    """
    Create a new product in the database.

    Args:
        producto (Producto): The Producto instance to add.

    Returns:
        Producto: The created Producto instance with refreshed state.
    """
    with Session(engine) as session:
        session.add(producto)
        session.commit()
        session.refresh(producto)
        return producto


def update_producto(producto_id: int, data: Producto, session: Session) -> Producto | None:
    """
    Update an existing product's attributes.

    Args:
        producto_id (int): The ID of the product to update.
        data (Producto): A Producto instance with updated attribute values.

    Returns:
        Producto | None: The updated Producto instance if found, otherwise None.
    """
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if not producto:
            return None

        producto.nombre = data.nombre
        producto.precio = data.precio
        producto.cantidad = data.cantidad
        producto.codigo_barra = data.codigo_barra
        producto.categoria_id = data.categoria_id
        producto.umbral_stock = data.umbral_stock

        session.commit()
        session.refresh(producto)
        return producto


def delete_producto(producto_id: int, session: Session) -> dict:
    """
    Delete a product from the database by ID.
    
    Args:
        producto_id (int): The ID of the product to delete.
        session (Session): SQLAlchemy session.
        
    Returns:
        dict: A dictionary with status information about the deletion.
    """
    # Verificar si el producto existe
    producto = session.get(Producto, producto_id)
    if not producto:
        return {"success": False, "message": "Producto no encontrado"}
    
    # Verificar si el producto está siendo utilizado en alguna orden
    from models.order import OrdenItem
    items_con_producto = session.exec(
        select(OrdenItem).where(OrdenItem.producto_id == producto_id)
    ).first()
    
    if items_con_producto:
        # El producto está en uso y no se puede eliminar
        return {
            "success": False, 
            "message": "No se puede eliminar el producto porque está asociado a órdenes existentes."
        }
    
    # Si no está siendo utilizado, proceder con la eliminación
    try:
        session.delete(producto)
        session.commit()
        return {"success": True, "message": "Producto eliminado correctamente"}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error al eliminar el producto: {str(e)}"}