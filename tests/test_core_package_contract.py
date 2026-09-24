from __future__ import annotations

import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PKGBUILD = ROOT / "packaging" / "arch" / "PKGBUILD"
SMOKE = ROOT / "packaging" / "arch" / "smoke-test.sh"
SERVICE = ROOT / "packaging" / "systemd" / "user" / "mnemosyne.service"
ARCH_SERVICE = ROOT / "packaging" / "arch" / "mnemosyne.service"
SETUPTOOLS_PATCH = ROOT / "packaging" / "arch" / "setuptools-arch-compat.patch"
ADR = ROOT / "docs" / "adr" / "0002-authoritative-core-package.md"
README = ROOT / "README.md"
WORKFLOW = ROOT / ".github" / "workflows" / "package-core.yml"

VERSION = "0.9.8"
COMMIT = "bbaffde0b8cd8fca2ff08a3cec08d2e763c76982"
ARCHIVE_URL = (
    "https://codeload.github.com/atxgreene/Mnemosyne/tar.gz/"
    "bbaffde0b8cd8fca2ff08a3cec08d2e763c76982"
)
ARCHIVE_SHA256 = "1626eae4bfe8efbf5d38e60e171db515da880d703c293b0a2fcee58a9d52920c"
SETUPTOOLS_PATCH_SHA256 = "8869389e4b79cc879ee4758f84afc466dff74741fbc869571bb541f6eb2826ad"
SETUPTOOLS_PATCH_TEXT = (
    '--- a/pyproject.toml\n'
    '+++ b/pyproject.toml\n'
    '@@ -1,3 +1,3 @@\n'
    ' [build-system]\n'
    '-requires = ["setuptools==80.9.0"]\n'
    '+requires = ["setuptools>=80.9.0,<85"]\n'
    ' build-backend = "setuptools.build_meta"\n'
)
TIER_CONSTANTS = (
    "L0_INSTINCT",
    "L1_HOT",
    "L2_WARM",
    "L3_COLD",
    "L4_PATTERN",
    "L5_IDENTITY",
)
TIER_STATS = (
    "L0_instinct",
    "L1_hot",
    "L2_warm",
    "L3_cold",
    "L4_pattern",
    "L5_identity",
)


def _text(path: Path) -> str:
    assert path.is_file(), f"missing {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _workflow_event_paths(text: str, event: str) -> set[str]:
    match = re.search(
        rf"(?ms)^  {re.escape(event)}:\n.*?^    paths:\n"
        rf"(?P<paths>(?:^      - [^\n]+\n)+)",
        text,
    )
    assert match, f"missing {event} path filters"
    return {
        line.removeprefix("- ").strip("'\"")
        for line in map(str.strip, match.group("paths").splitlines())
    }


def test_pkgbuild_builds_the_pinned_authoritative_source_archive() -> None:
    text = _text(PKGBUILD)
    for expected in (VERSION, COMMIT, ARCHIVE_URL, ARCHIVE_SHA256):
        assert expected in text
    assert "pkgname=mnemosyne-core" in text
    assert "python -m build --wheel --no-isolation" in text
    assert 'python -m installer --destdir="$pkgdir"' in text
    assert "../systemd/user/mnemosyne.service" not in text
    assert "  'mnemosyne.service'" in text
    assert "  'setuptools-arch-compat.patch'" in text
    assert '"$srcdir/mnemosyne.service"' in text
    service_sha256 = hashlib.sha256(SERVICE.read_bytes()).hexdigest()
    assert service_sha256 in text
    assert SETUPTOOLS_PATCH_SHA256 in text
    assert re.search(
        r'(?ms)^prepare\(\) \{\n'
        r'  cd "Mnemosyne-\$\{_commit\}"\n'
        r'  patch -Np1 -i "\$srcdir/setuptools-arch-compat.patch"\n'
        r'\}$',
        text,
    )
    assert "mnemosyne_harness-0.9.8-py3-none-any.whl" not in text
    assert "32ceeec5380b01eb1d0692c5c17c3b94bfbeb00b56fc2cdfdad3087f7bd5f0a9" not in text
    assert "curl " not in text


def test_arch_service_copy_is_exact_and_checksum_locked() -> None:
    assert ARCH_SERVICE.is_file()
    assert ARCH_SERVICE.read_bytes() == SERVICE.read_bytes()
    service_sha256 = hashlib.sha256(SERVICE.read_bytes()).hexdigest()
    assert PKGBUILD.read_text(encoding="utf-8").count(service_sha256) == 1


def test_setuptools_patch_is_exact_build_metadata_only_and_checksum_locked() -> None:
    patch_text = _text(SETUPTOOLS_PATCH)
    assert patch_text == SETUPTOOLS_PATCH_TEXT
    assert hashlib.sha256(SETUPTOOLS_PATCH.read_bytes()).hexdigest() == SETUPTOOLS_PATCH_SHA256
    assert PKGBUILD.read_text(encoding="utf-8").count(SETUPTOOLS_PATCH_SHA256) == 1

    changed_files = re.findall(r"^(?:--- a/|\+\+\+ b/)(.+)$", patch_text, re.MULTILINE)
    assert changed_files == ["pyproject.toml", "pyproject.toml"]
    changed_lines = [
        line
        for line in patch_text.splitlines()
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    ]
    assert changed_lines == [
        '-requires = ["setuptools==80.9.0"]',
        '+requires = ["setuptools>=80.9.0,<85"]',
    ]


def test_arch_smoke_exercises_installed_distribution_and_runtime() -> None:
    text = _text(SMOKE)
    assert 'version("mnemosyne-harness")' in text
    assert VERSION in text
    for symbol in TIER_CONSTANTS + TIER_STATS:
        assert symbol in text
    for required in (
        "MemoryStore",
        "fts5_enabled",
        "sqlite_master",
        "mnemosyne-memory",
        "mnemosyne-serve",
        "/healthz",
        "/stats",
        "/ui",
        "importlib.metadata",
        "distribution(\"mnemosyne-harness\")",
        "mnemosyne/core/memory.py",
        "PYTHONPATH",
    ):
        assert required in text
    assert "127.0.0.1" in text
    assert "0.0.0.0" not in text


def test_user_service_is_loopback_only_explicit_and_not_auto_enabled() -> None:
    text = _text(SERVICE)
    for required in (
        "[Unit]",
        "[Service]",
        "[Install]",
        "ExecStart=/usr/bin/mnemosyne-serve",
        "--host=127.0.0.1",
        "--projects-dir=%S/mnemosyne",
        "--apply-every=off",
        "Environment=MNEMOSYNE_PROJECTS_DIR=%S/mnemosyne",
        "StateDirectory=mnemosyne",
        "NoNewPrivileges=true",
        "ProtectSystem=strict",
        "WantedBy=default.target",
    ):
        assert required in text
    assert "enable" not in text.lower()
    assert "0.0.0.0" not in text


def test_adr_declares_one_immutable_core_without_overstating_phase_one() -> None:
    text = _text(ADR).lower()
    for phrase in (
        "atxgreene/mnemosyne",
        "sole authoritative l0–l5 implementation",
        "exact commit",
        "sha-256",
        "does not fork or copy cognition",
        "historical compatibility fixture",
        "fastapi",
        "jsonl",
        "debian live iso",
        "remains runnable",
        "pending later migration",
        "phase 1 does not",
        "thin adapter",
        "owned image",
    ):
        assert phrase in text, phrase


def test_readme_separates_phase_one_package_from_legacy_and_future_work() -> None:
    text = _text(README).lower()
    for phrase in (
        "phase 1",
        "mnemosyne-core",
        "authoritative l0–l5 core",
        "v0.9.8",
        "upstream/mnemosyne-core.lock.json",
        "packaging/arch/pkgbuild",
        "packaging/systemd/user/mnemosyne.service",
        "historical compatibility fixture",
        "remains runnable",
        "future thin omarchy adapter",
        "future owned image",
    ):
        assert phrase in text, phrase
    assert "the package does not install or replace the legacy fixture" in text


def test_package_workflow_is_pinned_least_privilege_and_complete() -> None:
    text = _text(WORKFLOW)
    assert "permissions:\n  contents: read" in text
    action_refs = re.findall(r"uses:\s+[^\s@]+@([^\s#]+)", text)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs), action_refs
    assert "persist-credentials: false" in text
    for command in (
        "pytest tests/test_core_package_contract.py tests/test_core_supply_chain.py",
        "pytest tests",
        "makepkg",
        "smoke-test.sh",
        "actions/upload-artifact",
    ):
        assert command in text
    assert re.search(r"archlinux:base[^\s]*@sha256:[0-9a-f]{64}", text)
    assert "retention-days: 7" in text

    required_paths = {
        ".github/workflows/package-core.yml",
        "docs/adr/0002-authoritative-core-package.md",
        "packaging/arch/**",
        "packaging/systemd/user/**",
        "tests/test_core_package_contract.py",
        "tests/test_core_supply_chain.py",
        "upstream/mnemosyne-core.lock.json",
        "upstream/NOTICE-MNEMOSYNE-CORE.md",
        "README.md",
    }
    for event in ("pull_request", "push"):
        assert required_paths <= _workflow_event_paths(text, event)
