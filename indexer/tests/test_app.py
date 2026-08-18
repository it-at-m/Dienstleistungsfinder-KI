import app


def test_missing_qdrant_configuration_fails(monkeypatch):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)
    assert app.main() != 0


def test_qdrant_connection_failure_fails(monkeypatch):
    monkeypatch.setenv("QDRANT_URL", "https://qdrant.example.invalid")
    monkeypatch.setenv("QDRANT_API_KEY", "test")
    monkeypatch.setattr(app, "QdrantClient", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("offline")))
    assert app.main() != 0
