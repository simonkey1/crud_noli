from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from utils.cache import cached, invalidate_cache

from db.database import engine
from models.models import Producto


@cached(ttl=180, cache_key_prefix="productos_all")
def get_all_productos(session: Session) -> list[Producto]:
    """
    Retrieve all products from the database with cache, including their associated categories.
    Cache TTL: 3 minutos para balance entre performance y datos actualizados.

    Returns:
        list[Producto]: A list of Producto instances with all fields including costo and margen.
    """
    statement = (
        select(Producto)
        .options(selectinload(Producto.categoria))
        .order_by(Producto.categoria_id.asc(), Producto.nombre.asc())  # Ordenamiento optimizado
    )
    productos = session.exec(statement).all()
    
    # Asegurarnos de que costo y margen estén incluidos en la respuesta
    for p in productos:
        if hasattr(p, "costo") and p.costo is None:
            p.costo = 0.0
        if hasattr(p, "margen") and p.margen is None:
            p.margen = 0.0
            
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
        producto = session.get(Producto, producto_id)
        
        # Asegurarnos de que costo y margen estén incluidos en la respuesta
        if producto:
            if hasattr(producto, "costo") and producto.costo is None:
                producto.costo = 0.0
            if hasattr(producto, "margen") and producto.margen is None:
                producto.margen = 0.0
                
        return producto


def create_producto(producto: Producto, session: Session) -> Producto:
    """
    Create a new product in the database with cache invalidation.

    Args:
        producto (Producto): The Producto instance to add.

    Returns:
        Producto: The created Producto instance with refreshed state.
    """
    # Validación previa: codigo_barra duplicado (si no es nulo/ vacío)
    if producto.codigo_barra:
        existing = session.exec(
            select(Producto).where(Producto.codigo_barra == producto.codigo_barra)
        ).first()
        if existing:
            raise ValueError("Ya existe un producto con este código de barras")

    try:
        session.add(producto)
        session.commit()
        session.refresh(producto)
        
        # Invalidar cache después de crear producto
        invalidate_cache("productos_all")
        invalidate_cache("pos_products")
        invalidate_cache("pos_search")
        
        return producto
    except IntegrityError as e:
        session.rollback()
        # Respaldo por si la validación previa no capturó una condición de carrera
        raise ValueError("Ya existe un producto con este código de barras") from e


def update_producto(producto_id: int, data: Producto, session: Session) -> Producto | None:
    """
    Update an existing product's attributes with cache invalidation.

    Args:
        producto_id (int): The ID of the product to update.
        data (Producto): A Producto instance with updated attribute values.

    Returns:
        Producto | None: The updated Producto instance if found, otherwise None.
    """
    # Validar duplicado de codigo_barra (si cambia y no es nulo/ vacío)
    if data.codigo_barra:
        dup = session.exec(
            select(Producto).where(
                (Producto.codigo_barra == data.codigo_barra) & (Producto.id != producto_id)
            )
        ).first()
        if dup:
            raise ValueError("Ya existe otro producto con este código de barras")

    producto = session.get(Producto, producto_id)
    if not producto:
        return None

    # Actualizar campos
    producto.nombre = data.nombre
    producto.precio = data.precio
    producto.cantidad = data.cantidad
    producto.codigo_barra = data.codigo_barra
    producto.categoria_id = data.categoria_id
    producto.umbral_stock = data.umbral_stock
    producto.costo = data.costo
    producto.margen = data.margen

    try:
        session.commit()
        session.refresh(producto)
        
        # Invalidar cache después de actualizar producto
        invalidate_cache("productos_all")
        invalidate_cache("pos_products")
        invalidate_cache("pos_search")
        
        return producto
    except IntegrityError as e:
        session.rollback()
        raise ValueError("Ya existe otro producto con este código de barras") from e


def delete_producto(producto_id: int, session: Session) -> dict:
    """
    Delete a product from the database by ID with cache invalidation.
    
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
    
    try:
        session.delete(producto)
        session.commit()
        
        # Invalidar cache después de eliminar producto
        invalidate_cache("productos_all")
        invalidate_cache("pos_products")
        invalidate_cache("pos_search")
        
        return {"success": True, "message": "Producto eliminado exitosamente"}
    except Exception as e:
        session.rollback()
        return {"success": False, "message": f"Error al eliminar producto: {str(e)}"}
        session.rollback()
        return {"success": False, "message": f"Error al eliminar el producto: {str(e)}"}