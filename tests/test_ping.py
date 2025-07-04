import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test del endpoint de salud"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_ping_valid_host():
    """Test de ping a un host válido"""
    response = client.get("/ping?host=8.8.8.8&count=2")
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "8.8.8.8"
    assert data["packets_transmitted"] == 2
    assert "packet_loss" in data
    assert "avg_ms" in data

def test_ping_invalid_host():
    """Test de ping a un host no permitido"""
    response = client.get("/ping?host=malicious.com&count=2")
    assert response.status_code == 400
    data = response.json()
    assert "no está permitido" in data["detail"]

def test_ping_invalid_count():
    """Test de ping con count inválido"""
    response = client.get("/ping?host=8.8.8.8&count=20")
    assert response.status_code == 422

def test_traceroute_valid_host():
    """Test de traceroute a un host válido"""
    response = client.get("/traceroute?host=google.com&max_hops=10")
    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "google.com"
    assert "hops" in data
    assert isinstance(data["hops"], list)

def test_allowed_hosts():
    """Test del endpoint de hosts permitidos"""
    response = client.get("/allowed-hosts")
    assert response.status_code == 200
    data = response.json()
    assert "allowed_hosts" in data
    assert isinstance(data["allowed_hosts"], list)
    assert len(data["allowed_hosts"]) > 0

def test_bulk_ping():
    """Test de ping masivo"""
    response = client.post("/ping/bulk?hosts=8.8.8.8&hosts=1.1.1.1&count=2")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2

def test_bulk_ping_too_many_hosts():
    """Test de ping masivo con demasiados hosts"""
    hosts = ["8.8.8.8"] * 10
    query = "&".join([f"hosts={host}" for host in hosts])
    response = client.post(f"/ping/bulk?{query}&count=2")
    assert response.status_code == 400
    data = response.json()
    assert "Máximo 5 hosts" in data["detail"]

def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"