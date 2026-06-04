from __future__ import annotations

import json
import math
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORD_RE = re.compile(r"[a-z0-9]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tokenize(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


@dataclass
class MemoryEntry:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            id=data.get("id") or uuid.uuid4().hex,
            content=data.get("content", ""),
            metadata=data.get("metadata") or {},
            created_at=data.get("created_at") or utc_now(),
        )


class MemoryStore:
    """Small local-first JSONL memory store for the v0.1 Mnemosyne OS scaffold."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def add_memory(self, content: str, metadata: dict[str, Any] | None = None) -> MemoryEntry:
        entry = MemoryEntry(content=content.strip(), metadata=metadata or {})
        if not entry.content:
            raise ValueError("memory content cannot be empty")
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return entry

    def all(self) -> list[MemoryEntry]:
        entries: list[MemoryEntry] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(MemoryEntry.from_dict(json.loads(line)))
        return entries

    def search(self, query: str, limit: int = 8) -> list[MemoryEntry]:
        query_terms = tokenize(query)
        if not query_terms:
            return list(reversed(self.all()))[:limit]

        scored: list[tuple[float, int, MemoryEntry]] = []
        for index, entry in enumerate(self.all()):
            haystack = " ".join([entry.content, " ".join(map(str, entry.metadata.values()))])
            terms = tokenize(haystack)
            overlap = len(query_terms & terms)
            if overlap:
                score = overlap / math.sqrt(max(len(terms), 1))
                scored.append((score, index, entry))
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return [entry for _, _, entry in scored[:limit]]

    def graph(self) -> dict[str, list[dict[str, Any]]]:
        entries = self.all()
        nodes = [
            {
                "id": entry.id,
                "label": entry.metadata.get("domain") or entry.content[:36],
                "title": entry.content,
                "domain": entry.metadata.get("domain", "general"),
                "created_at": entry.created_at,
            }
            for entry in entries
        ]
        edges: list[dict[str, Any]] = []
        for i, left in enumerate(entries):
            for right in entries[i + 1 :]:
                shared_domain = left.metadata.get("domain") and left.metadata.get("domain") == right.metadata.get("domain")
                shared_terms = tokenize(left.content) & tokenize(right.content)
                if shared_domain or len(shared_terms) >= 2:
                    edges.append(
                        {
                            "source": left.id,
                            "target": right.id,
                            "weight": 2 if shared_domain else 1,
                            "reason": "shared_domain" if shared_domain else "shared_terms",
                        }
                    )
        return {"nodes": nodes, "edges": edges}

    def stats(self) -> dict[str, Any]:
        entries = self.all()
        domains: dict[str, int] = {}
        for entry in entries:
            domain = str(entry.metadata.get("domain", "general"))
            domains[domain] = domains.get(domain, 0) + 1
        return {"total_entries": len(entries), "domains": domains}
