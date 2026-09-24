#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=""
python_bin="${PYTHON:-python}"
workdir="$(mktemp -d "${TMPDIR:-/tmp}/mnemosyne-core-smoke.XXXXXX")"
server_pid=""

cleanup() {
  status=$?
  if [[ -n "$server_pid" ]] && kill -0 "$server_pid" 2>/dev/null; then
    kill -TERM "$server_pid" 2>/dev/null || true
    wait "$server_pid" 2>/dev/null || true
  fi
  if [[ $status -ne 0 ]] && [[ -f "$workdir/server.log" ]]; then
    printf '%s\n' '--- mnemosyne-serve log ---' >&2
    command cat "$workdir/server.log" >&2
  fi
  rm -rf "$workdir"
  exit "$status"
}
trap cleanup EXIT INT TERM

command -v mnemosyne-memory >/dev/null
command -v mnemosyne-serve >/dev/null
mnemosyne-memory --help >/dev/null
mnemosyne-serve --help >/dev/null

SMOKE_DIR="$workdir" "$python_bin" - <<'PY'
import importlib.metadata
import os
import sqlite3
from pathlib import Path

from mnemosyne_memory import (
    L0_INSTINCT,
    L1_HOT,
    L2_WARM,
    L3_COLD,
    L4_PATTERN,
    L5_IDENTITY,
    MemoryStore,
)

assert importlib.metadata.version("mnemosyne-harness") == "0.9.8"
distribution = importlib.metadata.distribution("mnemosyne-harness")
installed_files = {
    str(path).replace("\\", "/") for path in (distribution.files or ())
}
assert "mnemosyne/core/memory.py" not in installed_files
assert not any(path.startswith("mnemosyne/") for path in installed_files)

constants = (
    L0_INSTINCT,
    L1_HOT,
    L2_WARM,
    L3_COLD,
    L4_PATTERN,
    L5_IDENTITY,
)
assert constants == (0, 1, 2, 3, 4, 5)
expected_tiers = {
    "L0_instinct",
    "L1_hot",
    "L2_warm",
    "L3_cold",
    "L4_pattern",
    "L5_identity",
}

db_path = Path(os.environ["SMOKE_DIR"]) / "memory.db"
with MemoryStore(path=db_path) as store:
    for tier in constants:
        store.write(
            f"phase one persistence sentinel tier {tier}",
            source="package-smoke",
            kind="fact",
            tier=tier,
        )
    stats = store.stats()
    assert stats["fts5_enabled"] is True, stats
    assert set(stats["by_tier"]) == expected_tiers, stats
    assert all(stats["by_tier"][name] == 1 for name in expected_tiers), stats

with sqlite3.connect(db_path) as conn:
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
        )
    }
assert {"memories", "memories_fts"} <= tables, tables

with MemoryStore(path=db_path) as reopened:
    hits = reopened.search("persistence sentinel tier 5", limit=10)
    assert any(hit["tier"] == L5_IDENTITY for hit in hits), hits
    assert reopened.stats()["total"] == 6
PY

port="$($python_bin - <<'PY'
import socket
with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
)"
projects_dir="$workdir/projects"
mkdir -p "$projects_dir"
MNEMOSYNE_PROJECTS_DIR="$projects_dir" mnemosyne-serve \
  --host=127.0.0.1 \
  --port="$port" \
  --projects-dir="$projects_dir" \
  --dream-every=off \
  --triage-every=off \
  --propose-every=off \
  --apply-every=off \
  >"$workdir/server.log" 2>&1 &
server_pid=$!

SMOKE_PORT="$port" "$python_bin" - <<'PY'
import json
import os
import time
from urllib.error import URLError
from urllib.request import urlopen

base = f"http://127.0.0.1:{os.environ['SMOKE_PORT']}"
last_error = None
for _ in range(100):
    try:
        with urlopen(base + "/healthz", timeout=1) as response:
            health = json.load(response)
        if health.get("status") == "ok":
            break
    except (OSError, URLError, ValueError) as error:
        last_error = error
        time.sleep(0.1)
else:
    raise AssertionError(f"server did not become healthy: {last_error}")

with urlopen(base + "/stats", timeout=2) as response:
    stats = json.load(response)
assert set(stats["memory"]["by_tier"]) == {
    "L0_instinct",
    "L1_hot",
    "L2_warm",
    "L3_cold",
    "L4_pattern",
    "L5_identity",
}

with urlopen(base + "/ui", timeout=2) as response:
    content_type = response.headers.get_content_type()
    body = response.read().decode("utf-8")
assert content_type == "text/html", content_type
assert "<!doctype html" in body.lower()
PY

kill -TERM "$server_pid"
wait "$server_pid"
server_pid=""
printf '%s\n' 'mnemosyne-core 0.9.8 smoke: PASS'
