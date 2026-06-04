from pathlib import Path

from mnemosyne.core.memory import MemoryStore
from mnemosyne.skills.store import SkillStore
from mnemosyne.tugboat.router import TugboatRouter


def test_memory_store_add_search_and_graph(tmp_path: Path):
    store = MemoryStore(tmp_path / "memory.jsonl")

    first = store.add_memory(
        content="Mantle convection connects geophysics and long-horizon modeling.",
        metadata={"domain": "geophysics", "importance": "high"},
    )
    second = store.add_memory(
        content="Stellas Hereditabimus is the continuity phrase for memory work.",
        metadata={"domain": "mythology", "importance": "medium"},
    )
    third = store.add_memory(
        content="Geophysics research benefits from persistent memory graphs.",
        metadata={"domain": "geophysics"},
    )

    assert first.id != second.id != third.id
    results = store.search("geophysics", limit=5)
    assert [entry.id for entry in results][:2] == [third.id, first.id]

    graph = store.graph()
    assert len(graph["nodes"]) == 3
    assert any(edge["source"] == first.id and edge["target"] == third.id for edge in graph["edges"])


def test_skill_store_seed_and_search(tmp_path: Path):
    skills = SkillStore(tmp_path / "skills.json")
    skills.add_skill(
        name="security_guardian",
        description="Review high-impact actions before execution.",
        triggers=["security", "approval", "dangerous command"],
        body="Check intent, scope, reversibility, and audit trail.",
    )

    found = skills.search("dangerous command")
    assert len(found) == 1
    assert found[0].name == "security_guardian"


def test_tugboat_router_uses_memory_and_skills(tmp_path: Path):
    memory = MemoryStore(tmp_path / "memory.jsonl")
    skills = SkillStore(tmp_path / "skills.json")
    memory.add_memory("Prior synthesis about geothermal vents and symbolism.", {"domain": "research"})
    skills.add_skill(
        name="research_synthesis",
        description="Synthesize multi-source research into a concise artifact.",
        triggers=["research", "synthesize", "sources"],
        body="Gather, compare, cite, and compress.",
    )

    route = TugboatRouter(memory, skills).route("Synthesize research on geothermal vents")

    assert route["goal"] == "Synthesize research on geothermal vents"
    assert route["memory_hits"]
    assert route["suggested_skills"][0]["name"] == "research_synthesis"
    assert "retrieve_memory" in route["steps"]
