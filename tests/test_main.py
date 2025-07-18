from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_returns_html():
     response = client.get("/")               # GET al root
     assert response.status_code == 200       # debe devolver 200 OK
   # ahora esperamos HTML, no JSON
     assert "<!DOCTYPE html>" in response.text