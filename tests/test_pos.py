import pytest
from fastapi.testclient import TestClient
from main import app
from db.dependencies import get_session
from models.models import Producto
from models.order import Orden, OrdenItem
from models.user import User
from sqlalchemy import delete, text
from sqlmodel import Session
from passlib.hash import bcrypt

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    session = next(get_session())
    # Limpieza de tablas usando la API delete()
    try:
        session.exec(delete(OrdenItem))
        session.exec(delete(Orden))
        session.exec(delete(Producto))
        session.exec(delete(User))
        session.commit()
    except Exception as e:
        print(f"Error al limpiar datos: {e}")
        session.rollback()
        
    # Crear usuario admin de prueba
    admin = User(
        username="admin",
        hashed_password=bcrypt.hash("admin"),
        is_active=True,
        is_superuser=True
    )
    session.add(admin)
    
    # Crear categoría para evitar violación de clave foránea
    from models.models import Categoria
    categoria = session.exec(text("SELECT id FROM categoria WHERE id = 1")).first()
    if not categoria:
        categoria = Categoria(id=1, nombre="Categoría Test")
        session.add(categoria)
        session.commit()
        
    # Crear producto inicial
    prod = Producto(
        id=1,
        nombre="Café Test",
        precio=1000,
        cantidad=10,
        categoria_id=1,
        codigo_barra="TEST"
    )
    session.add(prod)
    session.commit()
    yield
    # opcional: limpieza post-test si hace falta

def test_crear_orden_exito():
    payload = {
        "items": [{"producto_id": 1, "cantidad": 2}],
        "metodo_pago": "efectivo"
    }
    res = client.post("/pos/order", json=payload)
    print(f"Response status: {res.status_code}")
    print(f"Response body: {res.text}")
    assert res.status_code == 201
    body = res.json()
    assert body["total"] == 2000
    # Verificar decremento de stock
    prods = client.get("/pos/products").json()
    print(f"Productos después de la orden: {prods}")
    assert prods[0]["cantidad"] == 8

def test_crear_orden_stock_insuficiente():
    payload = {
        "items": [{"producto_id": 1, "cantidad": 20}],
        "metodo_pago": "debito"
    }
    
    try:
        res = client.post("/pos/order", json=payload)
        print(f"Response status: {res.status_code}")
        print(f"Response body: {res.text}")
        # Verificamos que se recibió un 400 y el mensaje correcto
        assert res.status_code == 400
        assert "Stock insuficiente" in res.text
    except Exception as e:
        # Si hay excepción, verificamos que es la esperada
        print(f"Excepción capturada: {type(e).__name__}: {str(e)}")
        assert "400: Stock insuficiente" in str(e)