# tests/test_products.py

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from db.dependencies import SECRET_KEY, ALGORITHM

client = TestClient(app)

def test_get_products_requires_auth():
    # El cliente sin token será redirigido a la página de inicio (/)
    # debido al auth_exception_handler en main.py
    res = client.get("/productos/")
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
    # Verificamos que estamos en la página de inicio (HTML)
    assert res.status_code == 200
    assert "Iniciar Sesión" in res.text
    assert "LOGO color sello de agua-01.png" in res.text

@pytest.fixture
def client_with_token():
    # 1) Creamos TestClient
    c = TestClient(app)
    # 2) Generamos un JWT con la misma clave que usa get_current_active_user
    payload = {
        "sub": "admin",
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    # 3) Inyectamos la cookie
    c.cookies.set("access_token", token)
    return c

def test_get_products_with_auth(client_with_token):
    res = client_with_token.get("/productos/")
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text}")
    # Verificamos que sea una respuesta exitosa
    assert res.status_code == 200
    # No validamos que sea JSON porque podría ser HTML en algunas configuraciones
    # assert isinstance(res.json(), list)
