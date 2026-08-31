import importlib.util
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import tomllib


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-python-runtime.py"


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_checker():
    spec = importlib.util.spec_from_file_location("check_python_runtime", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dependency_name(declaration: str) -> str:
    match = re.match(r"^([A-Za-z0-9_.-]+)", declaration.strip())
    assert match, declaration
    return match.group(1).lower().replace("_", "-")


def direct_requirement_names() -> set[str]:
    return {
        dependency_name(line)
        for line in read("requirements.in").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def test_pyproject_declares_exact_python_runtime_contract():
    metadata = tomllib.loads(read("pyproject.toml"))
    project = metadata["project"]

    assert project["name"] == "mnemosyne-os"
    assert project["version"] == "0.1.0"
    assert project["readme"] == "README.md"
    assert project["license"] == {"file": "LICENSE"}
    assert project["requires-python"] == ">=3.11"
    assert project["dependencies"] == ["fastapi", "pydantic", "starlette", "uvicorn"]
    assert project["optional-dependencies"] == {"test": ["pytest"]}
    assert "build-system" not in metadata


def test_pyproject_dependency_names_match_direct_requirements():
    project = tomllib.loads(read("pyproject.toml"))["project"]
    runtime_names = {dependency_name(item) for item in project["dependencies"]}
    test_names = {
        dependency_name(item)
        for item in project["optional-dependencies"]["test"]
    }

    assert runtime_names == {"fastapi", "pydantic", "starlette", "uvicorn"}
    assert test_names == {"pytest"}
    assert runtime_names | test_names == direct_requirement_names()


def test_runtime_helper_accepts_supported_and_future_python_3_versions():
    checker = load_checker()

    assert checker.runtime_error((3, 11, 0), "/python311") is None
    assert checker.runtime_error((3, 15, 2), "/future-python") is None


def test_runtime_helper_reports_precise_error_for_python_3_10():
    checker = load_checker()

    error = checker.runtime_error((3, 10, 14), "/opt/python3.10/bin/python")

    assert error is not None
    assert "requires Python >=3.11" in error
    assert "3.10.14" in error
    assert "/opt/python3.10/bin/python" in error


def test_runtime_helper_cli_succeeds_on_current_interpreter():
    checker = load_checker()

    assert checker.main() == (0 if sys.version_info >= (3, 11) else 1)


def test_local_installer_checks_selected_and_actual_venv_interpreters_before_pip():
    installer = read("scripts/install-local.sh")
    selected_check = '"$MNEMOSYNE_PYTHON" "$SCRIPT_DIR/check-python-runtime.py"'
    create_venv = '"$MNEMOSYNE_PYTHON" -m venv .venv'
    venv_check = '".venv/bin/python" "$SCRIPT_DIR/check-python-runtime.py"'
    pip_install = '".venv/bin/python" -m pip install --require-hashes -r requirements.txt'

    assert 'MNEMOSYNE_PYTHON="${MNEMOSYNE_PYTHON:-python3}"' in installer
    assert installer.index(selected_check) < installer.index(create_venv)
    assert installer.index(create_venv) < installer.index(venv_check)
    assert installer.index(venv_check) < installer.index(pip_install)


def test_local_installer_does_not_fall_back_to_external_pip_for_pipless_venv(tmp_path):
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    scripts_dir.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "install-local.sh", scripts_dir)
    shutil.copy2(CHECKER_PATH, scripts_dir)
    (repo / "requirements.txt").write_text("", encoding="utf-8")

    subprocess.run(
        [sys.executable, "-m", "venv", "--without-pip", repo / ".venv"],
        check=True,
        capture_output=True,
        text=True,
    )

    marker = tmp_path / "fallback-pip-invoked"
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    fallback_pip = fake_bin / "pip"
    fallback_pip.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$*" > "$FALLBACK_PIP_MARKER"\n',
        encoding="utf-8",
    )
    fallback_pip.chmod(0o755)

    env = os.environ.copy()
    env["MNEMOSYNE_PYTHON"] = sys.executable
    env["FALLBACK_PIP_MARKER"] = str(marker)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    result = subprocess.run(
        ["bash", scripts_dir / "install-local.sh"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )

    assert not marker.exists(), marker.read_text(encoding="utf-8") if marker.exists() else ""
    assert result.returncode != 0, result.stdout + result.stderr


def test_packaging_installer_fails_early_and_checks_actual_venv_before_pip():
    installer = read("packaging/install-mnemosyne-os.sh")
    system_check = '"$MNEMOSYNE_PYTHON" "$SOURCE_INPUT/scripts/check-python-runtime.py"'
    create_venv = '"$MNEMOSYNE_PYTHON" -m venv "$VENV_DIR"'
    venv_check = '"$VENV_DIR/bin/python" "$SOURCE_DIR/scripts/check-python-runtime.py"'
    pip_install = '"$VENV_DIR/bin/pip" install --require-hashes -r "$SOURCE_DIR/requirements.txt"'

    assert 'MNEMOSYNE_PYTHON="${MNEMOSYNE_PYTHON:-python3}"' in installer
    assert installer.index("apt-get install -y") < installer.index(system_check)
    assert installer.index(system_check) < installer.index("useradd --system")
    assert installer.index(system_check) < installer.index("rsync -a --delete")
    assert installer.index(system_check) < installer.index(create_venv)
    assert installer.index(create_venv) < installer.index(venv_check)
    assert installer.index(venv_check) < installer.index(pip_install)
    assert "--exclude '.venv*/'" in installer


def test_readme_documents_python_runtime_and_fail_fast_installers():
    readme = read("README.md")

    assert "Python 3.11+" in readme
    assert "fail fast" in readme.lower()
