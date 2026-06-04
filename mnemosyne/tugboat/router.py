from __future__ import annotations

from mnemosyne.core.memory import MemoryStore
from mnemosyne.skills.store import SkillStore


class TugboatRouter:
    """Declarative routing stub for the v0.1 cognitive-core scaffold."""

    def __init__(self, memory: MemoryStore, skills: SkillStore):
        self.memory = memory
        self.skills = skills

    def route(self, goal: str) -> dict:
        memory_hits = [entry.to_dict() for entry in self.memory.search(goal, limit=5)]
        suggested_skills = [skill.to_dict() for skill in self.skills.search(goal, limit=5)]
        steps = ["classify_goal"]
        if memory_hits:
            steps.append("retrieve_memory")
        if suggested_skills:
            steps.append("apply_relevant_skills")
        if any(word in goal.lower() for word in ["delete", "credential", "deploy", "sudo", "security"]):
            steps.append("security_guardian_review")
        steps.append("synthesize_response")
        return {
            "goal": goal,
            "route_type": "research_orchestration" if "research" in goal.lower() or "synthesize" in goal.lower() else "general",
            "steps": steps,
            "memory_hits": memory_hits,
            "suggested_skills": suggested_skills,
            "policy": {"safety_level": "high", "write_audit": True},
        }
