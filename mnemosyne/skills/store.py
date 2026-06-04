from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

WORD_RE = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> set[str]:
    return set(WORD_RE.findall(text.lower()))


@dataclass
class Skill:
    name: str
    description: str
    triggers: list[str]
    body: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        return cls(
            id=data.get("id") or uuid.uuid4().hex,
            name=data["name"],
            description=data.get("description", ""),
            triggers=list(data.get("triggers") or []),
            body=data.get("body", ""),
        )


class SkillStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def all(self) -> list[Skill]:
        raw = json.loads(self.path.read_text(encoding="utf-8") or "[]")
        return [Skill.from_dict(item) for item in raw]

    def save(self, skills: list[Skill]) -> None:
        self.path.write_text(json.dumps([s.to_dict() for s in skills], indent=2), encoding="utf-8")

    def add_skill(self, name: str, description: str, triggers: list[str], body: str) -> Skill:
        skills = [skill for skill in self.all() if skill.name != name]
        skill = Skill(name=name, description=description, triggers=triggers, body=body)
        skills.append(skill)
        self.save(skills)
        return skill

    def search(self, query: str, limit: int = 5) -> list[Skill]:
        query_terms = tokens(query)
        scored: list[tuple[int, Skill]] = []
        for skill in self.all():
            haystack = " ".join([skill.name, skill.description, " ".join(skill.triggers), skill.body])
            score = len(query_terms & tokens(haystack))
            if score:
                scored.append((score, skill))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [skill for _, skill in scored[:limit]]
