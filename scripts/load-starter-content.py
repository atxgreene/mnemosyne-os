from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mnemosyne.core.memory import MemoryStore
from mnemosyne.skills.store import SkillStore

HOME = Path(os.environ.get("MNEMOSYNE_HOME", Path.home() / ".mnemosyne"))


def main() -> None:
    memory = MemoryStore(HOME / "memory.jsonl")
    skills = SkillStore(HOME / "skills.json")

    existing_contents = {entry.content for entry in memory.all()}
    for item in json.loads((ROOT / "seed" / "starter_memories.json").read_text(encoding="utf-8")):
        if item["content"] not in existing_contents:
            memory.add_memory(item["content"], item.get("metadata", {}))

    existing_skills = {skill.name for skill in skills.all()}
    for item in json.loads((ROOT / "seed" / "starter_skills.json").read_text(encoding="utf-8")):
        if item["name"] not in existing_skills:
            skills.add_skill(item["name"], item.get("description", ""), item.get("triggers", []), item.get("body", ""))

    print(f"Seeded Mnemosyne home: {HOME}")


if __name__ == "__main__":
    main()
