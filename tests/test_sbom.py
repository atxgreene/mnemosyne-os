import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-python-sbom.py"


def test_python_sbom_is_valid_deterministic_cyclonedx(tmp_path):
    output = tmp_path / "sbom.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(output)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["bomFormat"] == "CycloneDX"
    assert document["specVersion"] == "1.5"
    assert document["version"] == 1
    assert document["metadata"]["component"]["name"] == "mnemosyne-os-python-environment"
    assert "timestamp" not in document["metadata"]
    components = document["components"]
    names = [component["name"] for component in components]
    assert names == sorted(set(names), key=str.casefold)
    assert "pytest" in {name.lower() for name in names}
    for component in components:
        assert component["type"] == "library"
        assert component["version"]
        assert component["purl"].startswith("pkg:pypi/")
