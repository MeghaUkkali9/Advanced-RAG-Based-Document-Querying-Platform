import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_home_ui():
    res = client.get("/")
    
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "Document Portal" in res.text 

def test_health_endpoint():
    res = client.get("/health")
    
    assert res.status_code == 200
    assert res.json() == {
        "status": "ok",
        "service": "Document Querying Platform"
    }