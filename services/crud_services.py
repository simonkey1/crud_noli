from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from db.database import engine
from models.models import Producto


def get_all_productos() -> list[Producto]:
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


def get_producto(producto_id: int) -> Producto | None:
    """
    Retrieve a single product by its ID.

    Args:
        producto_id (int): The ID of the product to retrieve.

    Returns:
        Producto | None: The Producto instance if found, otherwise None.
    """
    with Session(engine) as session:
        return session.get(Producto, producto_id)


def create_producto(producto: Producto) -> Producto:
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


def update_producto(producto_id: int, data: Producto) -> Producto | None:
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
        producto.image_url = data.image_url

        session.commit()
        session.refresh(producto)
        return producto


def delete_producto(producto_id: int) -> Producto | None:
    """
    Delete a product from the database by ID.

    Args:
        producto_id (int): The ID of the product to delete.

    Returns:
        Producto | None: The deleted Producto instance if found and deleted, otherwise None.
    """
    with Session(engine) as session:
        producto = session.get(Producto, producto_id)
        if producto:
            session.delete(producto)
            session.commit()
        return producto