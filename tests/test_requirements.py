from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_python_requirements_do_not_include_browser_npm_packages():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    normalized = {line.strip().split("==")[0].split(">=")[0] for line in requirements if line.strip() and not line.startswith("#")}
    assert "vis-network" not in normalized, "vis-network is an npm/browser library, not a pip package"
