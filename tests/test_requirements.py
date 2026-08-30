from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def requirement_names():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    return {match.group(1).lower() for match in re.finditer(r"(?m)^([A-Za-z0-9_.-]+)==", text)}


def test_python_requirements_include_test_runner():
    assert "pytest" in requirement_names()


def test_python_requirements_do_not_include_browser_npm_packages():
    assert "vis-network" not in requirement_names(), "vis-network is an npm/browser library, not a pip package"


def test_python_requirements_are_fully_pinned_and_hashed():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    records = re.split(r"(?m)(?=^[A-Za-z0-9_.-]+==)", text)
    packages = [record for record in records if re.match(r"^[A-Za-z0-9_.-]+==", record)]
    assert packages, "requirements.txt should contain pip-compiled package records"
    for record in packages:
        first_line = record.splitlines()[0]
        assert re.match(r"^[A-Za-z0-9_.-]+==[^\s\\]+", first_line), first_line
        assert "--hash=sha256:" in record, first_line


def test_direct_requirements_are_declared_separately():
    direct = (ROOT / "requirements.in").read_text(encoding="utf-8").splitlines()
    names = {line.strip().lower() for line in direct if line.strip() and not line.startswith("#")}
    assert names == {"fastapi", "uvicorn", "pydantic", "starlette", "pytest"}


def test_installers_enforce_hash_checking():
    for relative_path in (
        ".github/workflows/build-iso.yml",
        "packaging/install-mnemosyne-os.sh",
        "scripts/install-local.sh",
    ):
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "install --require-hashes -r" in source


def test_build_and_install_paths_do_not_upgrade_pip_from_an_unlocked_source():
    for relative_path in (
        ".github/workflows/build-iso.yml",
        "packaging/install-mnemosyne-os.sh",
        "scripts/install-local.sh",
    ):
        source = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "pip install --upgrade pip" not in source
