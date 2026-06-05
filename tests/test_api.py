import pytest
from pydantic import ValidationError

from mnemosyne.services import api_server


def test_api_memory_stats_and_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("MNEMOSYNE_HOME", str(tmp_path))

    with pytest.raises(ValidationError):
        api_server.MemoryAddRequest(content="", metadata={})

    created = api_server.add_memory(
        api_server.MemoryAddRequest(
            content="API validation improves local core reliability",
            metadata={"domain": "api"},
        )
    )
    assert created["metadata"]["domain"] == "api"

    memory_stats = api_server.memory_stats()
    assert memory_stats["total_entries"] == 1
    assert memory_stats["domains"] == {"api": 1}

    stats = api_server.stats()
    assert stats["memory"]["total_entries"] == 1
    assert "skills" in stats
