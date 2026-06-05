from fastapi.testclient import TestClient

from mnemosyne.services.api_server import app


def test_api_memory_stats_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("MNEMOSYNE_HOME", str(tmp_path))
    client = TestClient(app)

    empty = client.post("/memory/add", json={"content": "", "metadata": {}})
    assert empty.status_code == 422

    created = client.post(
        "/memory/add",
        json={"content": "API validation improves local core reliability", "metadata": {"domain": "api"}},
    )
    assert created.status_code == 200
    assert created.json()["metadata"]["domain"] == "api"

    memory_stats = client.get("/memory/stats")
    assert memory_stats.status_code == 200
    assert memory_stats.json()["total_entries"] == 1
    assert memory_stats.json()["domains"] == {"api": 1}

    stats = client.get("/stats")
    assert stats.status_code == 200
    assert stats.json()["memory"]["total_entries"] == 1
    assert "skills" in stats.json()
