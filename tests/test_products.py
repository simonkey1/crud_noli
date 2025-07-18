# tests/test_products.py

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from db.dependencies import SECRET_KEY, ALGORITHM

client = TestClient(app)

def test_get_products_requires_auth():
    res = client.get("/productos/")
    assert res.status_code == 401

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
    assert res.status_code == 200
    assert isinstance(res.json(), list)
