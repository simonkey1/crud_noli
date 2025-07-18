# tests/test_pos.py

import pytest
from fastapi.testclient import TestClient
from main import app
from db.dependencies import get_session
from models.models import Producto
from models.order import Orden, OrdenItem
from sqlalchemy import delete

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    session = next(get_session())
    # Limpieza de tablas usando la API delete()
    session.exec(delete(OrdenItem))
    session.exec(delete(Orden))
    session.exec(delete(Producto))
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
    assert res.status_code == 201
    body = res.json()
    assert body["total"] == 2000
    # Verificar decremento de stock
    prods = client.get("/pos/products").json()
    assert prods[0]["cantidad"] == 8

def test_crear_orden_stock_insuficiente():
    payload = {
        "items": [{"producto_id": 1, "cantidad": 20}],
        "metodo_pago": "debito"
    }
    res = client.post("/pos/order", json=payload)
    assert res.status_code == 400
    assert "Stock insuficiente" in res.text
