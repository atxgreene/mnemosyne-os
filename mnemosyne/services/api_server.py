from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mnemosyne.core.memory import MemoryStore
from mnemosyne.skills.store import SkillStore
from mnemosyne.tugboat.router import TugboatRouter


def mnemosyne_home() -> Path:
    configured = os.environ.get("MNEMOSYNE_HOME")
    if configured:
        return Path(configured)
    return Path.home() / ".mnemosyne"


def stores() -> tuple[MemoryStore, SkillStore]:
    home = mnemosyne_home()
    return MemoryStore(home / "memory.jsonl"), SkillStore(home / "skills.json")


app = FastAPI(title="Mnemosyne OS Cognitive Core", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MemoryAddRequest(BaseModel):
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RouteRequest(BaseModel):
    goal: str


class SkillAddRequest(BaseModel):
    name: str
    description: str
    triggers: list[str] = Field(default_factory=list)
    body: str = ""


@app.get("/health")
def health() -> dict[str, Any]:
    memory, skills = stores()
    return {"ok": True, "home": str(mnemosyne_home()), "memory": memory.stats(), "skills": len(skills.all())}


@app.post("/memory/add")
def add_memory(request: MemoryAddRequest) -> dict[str, Any]:
    memory, _ = stores()
    return memory.add_memory(request.content, request.metadata).to_dict()


@app.get("/memory/search")
def search_memory(query: str, limit: int = 8) -> list[dict[str, Any]]:
    memory, _ = stores()
    return [entry.to_dict() for entry in memory.search(query, limit)]


@app.get("/memory/graph")
def memory_graph() -> dict[str, Any]:
    memory, _ = stores()
    return memory.graph()


@app.get("/skills")
def list_skills(query: str | None = None) -> list[dict[str, Any]]:
    _, skills = stores()
    items = skills.search(query) if query else skills.all()
    return [skill.to_dict() for skill in items]


@app.post("/skills")
def add_skill(request: SkillAddRequest) -> dict[str, Any]:
    _, skills = stores()
    return skills.add_skill(request.name, request.description, request.triggers, request.body).to_dict()


@app.post("/tugboat/route")
def route(request: RouteRequest) -> dict[str, Any]:
    memory, skills = stores()
    return TugboatRouter(memory, skills).route(request.goal)
