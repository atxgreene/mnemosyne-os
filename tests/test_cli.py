import json
import subprocess
import sys
from pathlib import Path


def test_cli_store_search_route_and_graph(tmp_path: Path):
    cli = Path(__file__).resolve().parents[1] / "bin" / "mnemosyne"
    env = {"MNEMOSYNE_HOME": str(tmp_path)}

    store = subprocess.run(
        [sys.executable, str(cli), "store", "A memory about BCE physics", "--domain", "physics"],
        env={**env},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "stored" in store.stdout.lower()

    search = subprocess.run(
        [sys.executable, str(cli), "search", "physics", "--json"],
        env={**env},
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(search.stdout)
    assert payload[0]["metadata"]["domain"] == "physics"

    route = subprocess.run(
        [sys.executable, str(cli), "route", "Research BCE physics", "--json"],
        env={**env},
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(route.stdout)["goal"] == "Research BCE physics"

    graph = subprocess.run(
        [sys.executable, str(cli), "graph", "--json"],
        env={**env},
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(graph.stdout)["nodes"]
