import os

os.environ.setdefault("DLF_SESSION_SECRET", "test-session-secret")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "test-public")
os.environ.setdefault("LANGFUSE_SECRET_KEY", "test-secret")
os.environ.setdefault("LANGFUSE_HOST", "https://langfuse.example.invalid")

from backend import backend
from fastapi.testclient import TestClient

client = TestClient(backend)


def test_healthz():
    response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_static_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<dlf-search-webcomponent>" in response.text
    assert "Build the frontend or run the core container" not in response.text
