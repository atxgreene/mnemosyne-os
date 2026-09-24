from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "upstream" / "mnemosyne-core.lock.json"
NOTICE_PATH = ROOT / "upstream" / "NOTICE-MNEMOSYNE-CORE.md"
PKGBUILD_PATH = ROOT / "packaging" / "arch" / "PKGBUILD"

EXPECTED = {
    "repository": "atxgreene/Mnemosyne",
    "repository_url": "https://github.com/atxgreene/Mnemosyne",
    "version": "0.9.8",
    "tag": "v0.9.8",
    "commit_sha": "bbaffde0b8cd8fca2ff08a3cec08d2e763c76982",
    "archive_url": (
        "https://codeload.github.com/atxgreene/Mnemosyne/tar.gz/"
        "bbaffde0b8cd8fca2ff08a3cec08d2e763c76982"
    ),
    "archive_sha256": "1626eae4bfe8efbf5d38e60e171db515da880d703c293b0a2fcee58a9d52920c",
    "wheel_filename": "mnemosyne_harness-0.9.8-py3-none-any.whl",
    "wheel_url": (
        "https://github.com/atxgreene/Mnemosyne/releases/download/v0.9.8/"
        "mnemosyne_harness-0.9.8-py3-none-any.whl"
    ),
    "wheel_sha256": "32ceeec5380b01eb1d0692c5c17c3b94bfbeb00b56fc2cdfdad3087f7bd5f0a9",
    "license_url": (
        "https://raw.githubusercontent.com/atxgreene/Mnemosyne/"
        "bbaffde0b8cd8fca2ff08a3cec08d2e763c76982/LICENSE"
    ),
    "license_sha256": "3f4582bcef89d07c0504ed023dad80cdb526bf529bd4e8fb04a87e19332ab3b7",
}
TOP_KEYS = {"pin_policy", "schema", "schema_version", "upstreams"}
POLICY_KEYS = {"execution_authority", "mutable_refs"}
AUTHORITY_KEYS = {"commit_field", "integrity_field", "policy"}
UPSTREAM_KEYS = {
    "commit_sha",
    "license",
    "name",
    "release",
    "repository",
    "repository_url",
    "role",
    "source_archive",
}
ARCHIVE_KEYS = {"sha256", "url"}
RELEASE_KEYS = {"tag", "version", "wheel"}
WHEEL_KEYS = {"filename", "sha256", "url"}
LICENSE_KEYS = {"sha256", "source_url", "spdx_id"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")


def load_lock() -> dict:
    assert LOCK_PATH.is_file(), f"missing {LOCK_PATH.relative_to(ROOT)}"
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def _closed(actual: object, expected: set[str], where: str, errors: list[str]) -> bool:
    if not isinstance(actual, dict):
        errors.append(f"{where}: expected object")
        return False
    actual_keys = set(actual)
    for key in sorted(expected - actual_keys):
        errors.append(f"{where}: missing field {key}")
    for key in sorted(actual_keys - expected):
        errors.append(f"{where}: unknown field {key}")
    return actual_keys == expected


def validate_lock(document: dict) -> list[str]:
    errors: list[str] = []
    if not _closed(document, TOP_KEYS, "lock", errors):
        return errors
    if document["schema"] != "mnemosyne.authoritative-core-lock":
        errors.append("unexpected schema")
    if document["schema_version"] != 1:
        errors.append("unexpected schema version")

    policy = document["pin_policy"]
    if _closed(policy, POLICY_KEYS, "pin_policy", errors):
        authority = policy["execution_authority"]
        if _closed(authority, AUTHORITY_KEYS, "execution_authority", errors):
            if authority != {
                "commit_field": "upstreams[].commit_sha",
                "integrity_field": "upstreams[].source_archive.sha256",
                "policy": "exact_commit_and_sha256",
            }:
                errors.append("execution authority must be exact commit+hash")
        if policy["mutable_refs"] != "metadata_only":
            errors.append("mutable refs must be metadata only")

    upstreams = document["upstreams"]
    if not isinstance(upstreams, list):
        return errors + ["upstreams must be a list"]
    if len(upstreams) != 1:
        errors.append(f"mnemosyne-core: expected exactly one entry, found {len(upstreams)}")
    names = [item.get("name") for item in upstreams if isinstance(item, dict)]
    if names != ["mnemosyne-core"]:
        errors.append(f"unexpected upstream sequence: {names!r}")

    for item in upstreams:
        if not _closed(item, UPSTREAM_KEYS, "upstream", errors):
            continue
        if item["name"] != "mnemosyne-core":
            errors.append("unexpected upstream name")
        if item["repository"] != EXPECTED["repository"]:
            errors.append("unexpected canonical repository")
        if item["repository_url"] != EXPECTED["repository_url"]:
            errors.append("unexpected canonical repository URL")
        if item["role"] != "sole authoritative L0-L5 cognitive core implementation":
            errors.append("unexpected authoritative role")
        if not SHA40_RE.fullmatch(item["commit_sha"] or ""):
            errors.append("commit is not exact 40-hex")
        if item["commit_sha"] != EXPECTED["commit_sha"]:
            errors.append("unexpected verified commit")

        archive = item["source_archive"]
        if _closed(archive, ARCHIVE_KEYS, "source_archive", errors):
            if not SHA256_RE.fullmatch(archive["sha256"] or ""):
                errors.append("archive SHA-256 is malformed")
            if archive["url"] != EXPECTED["archive_url"]:
                errors.append("unexpected commit-pinned archive URL")
            if archive["sha256"] != EXPECTED["archive_sha256"]:
                errors.append("unexpected verified archive SHA-256")
            if item["commit_sha"] not in archive["url"]:
                errors.append("archive URL does not match commit")

        release = item["release"]
        if _closed(release, RELEASE_KEYS, "release", errors):
            if release["version"] != EXPECTED["version"]:
                errors.append("unexpected version")
            if release["tag"] != EXPECTED["tag"]:
                errors.append("unexpected tag metadata")
            wheel = release["wheel"]
            if _closed(wheel, WHEEL_KEYS, "release.wheel", errors):
                if wheel["filename"] != EXPECTED["wheel_filename"]:
                    errors.append("unexpected wheel filename")
                if wheel["url"] != EXPECTED["wheel_url"]:
                    errors.append("unexpected release wheel URL")
                if wheel["sha256"] != EXPECTED["wheel_sha256"]:
                    errors.append("unexpected verified wheel SHA-256")
                if not SHA256_RE.fullmatch(wheel["sha256"] or ""):
                    errors.append("wheel SHA-256 is malformed")

        license_record = item["license"]
        if _closed(license_record, LICENSE_KEYS, "license", errors):
            if license_record["spdx_id"] != "MIT":
                errors.append("license is not MIT")
            if license_record["source_url"] != EXPECTED["license_url"]:
                errors.append("unexpected commit-pinned license URL")
            if license_record["sha256"] != EXPECTED["license_sha256"]:
                errors.append("unexpected verified license SHA-256")
            if not SHA256_RE.fullmatch(license_record["sha256"] or ""):
                errors.append("license SHA-256 is malformed")
            if item["commit_sha"] not in license_record["source_url"]:
                errors.append("license URL does not match commit")
    return errors


def notice_license_body(notice: str) -> str:
    matches = re.findall(
        r"(?ms)^## Pinned MIT license text\n.*?^```text\n(?P<body>.*?)\n```[ \t]*(?:\n|\Z)",
        notice,
    )
    assert len(matches) == 1, f"expected one pinned license body, found {len(matches)}"
    return matches[0].rstrip("\n") + "\n"


def validate_pkgbuild_against_lock(document: dict, pkgbuild: str) -> list[str]:
    item = document["upstreams"][0]
    expected_assignments = {
        "pkgver": item["release"]["version"],
        "_commit": item["commit_sha"],
        "_archive_url": item["source_archive"]["url"],
    }
    errors = []
    for name, expected in expected_assignments.items():
        match = re.search(rf"(?m)^{re.escape(name)}=(?:'([^']*)'|([^\n]+))$", pkgbuild)
        actual = (match.group(1) or match.group(2)) if match else None
        if actual != expected:
            errors.append(f"PKGBUILD {name} drift")
    checksum = item["source_archive"]["sha256"]
    if pkgbuild.count(checksum) != 1:
        errors.append("PKGBUILD source archive SHA-256 drift")
    return errors


def test_lock_is_closed_valid_and_deterministic() -> None:
    document = load_lock()
    assert not validate_lock(document), validate_lock(document)
    assert LOCK_PATH.read_text(encoding="utf-8") == json.dumps(
        document, indent=2, sort_keys=True
    ) + "\n"


def test_lock_rejects_unknown_missing_and_duplicate_records() -> None:
    document = load_lock()
    unknown = copy.deepcopy(document)
    unknown["surprise"] = True
    assert "lock: unknown field surprise" in validate_lock(unknown)

    missing = copy.deepcopy(document)
    missing["upstreams"][0]["source_archive"].pop("sha256")
    assert "source_archive: missing field sha256" in validate_lock(missing)

    duplicate = copy.deepcopy(document)
    duplicate["upstreams"].append(copy.deepcopy(duplicate["upstreams"][0]))
    assert any("expected exactly one entry" in error for error in validate_lock(duplicate))


def test_lock_rejects_mutable_execution_authority() -> None:
    document = load_lock()
    mutated = copy.deepcopy(document)
    mutated["pin_policy"]["execution_authority"] = {
        "commit_field": "upstreams[].release.tag",
        "integrity_field": "upstreams[].release.wheel.sha256",
        "policy": "tag_and_sha256",
    }
    mutated["pin_policy"]["mutable_refs"] = "allowed"
    errors = validate_lock(mutated)
    assert "execution authority must be exact commit+hash" in errors
    assert "mutable refs must be metadata only" in errors


def test_lock_rejects_mutable_source_and_license_urls() -> None:
    mutated = copy.deepcopy(load_lock())
    item = mutated["upstreams"][0]
    item["source_archive"]["url"] = (
        "https://codeload.github.com/atxgreene/Mnemosyne/tar.gz/refs/tags/v0.9.8"
    )
    item["license"]["source_url"] = (
        "https://raw.githubusercontent.com/atxgreene/Mnemosyne/v0.9.8/LICENSE"
    )
    errors = validate_lock(mutated)
    assert "unexpected commit-pinned archive URL" in errors
    assert "archive URL does not match commit" in errors
    assert "unexpected commit-pinned license URL" in errors
    assert "license URL does not match commit" in errors


def test_lock_rejects_coherent_commit_url_and_hash_mutation() -> None:
    document = load_lock()
    mutated = copy.deepcopy(document)
    item = mutated["upstreams"][0]
    replacement = "0" * 40
    item["commit_sha"] = replacement
    item["source_archive"] = {
        "url": f"https://codeload.github.com/atxgreene/Mnemosyne/tar.gz/{replacement}",
        "sha256": "1" * 64,
    }
    item["license"] = {
        "spdx_id": "MIT",
        "source_url": (
            "https://raw.githubusercontent.com/atxgreene/Mnemosyne/"
            f"{replacement}/LICENSE"
        ),
        "sha256": "2" * 64,
    }
    errors = validate_lock(mutated)
    assert "unexpected verified commit" in errors
    assert "unexpected verified archive SHA-256" in errors
    assert "unexpected verified license SHA-256" in errors


def test_lock_rejects_coherent_release_wheel_mutation() -> None:
    mutated = copy.deepcopy(load_lock())
    release = mutated["upstreams"][0]["release"]
    release["version"] = "0.9.9"
    release["tag"] = "v0.9.9"
    release["wheel"] = {
        "filename": "mnemosyne_harness-0.9.9-py3-none-any.whl",
        "url": (
            "https://github.com/atxgreene/Mnemosyne/releases/download/v0.9.9/"
            "mnemosyne_harness-0.9.9-py3-none-any.whl"
        ),
        "sha256": "3" * 64,
    }
    errors = validate_lock(mutated)
    assert "unexpected version" in errors
    assert "unexpected tag metadata" in errors
    assert "unexpected verified wheel SHA-256" in errors


def test_pkgbuild_cannot_drift_from_lock() -> None:
    item = load_lock()["upstreams"][0]
    pkgbuild = PKGBUILD_PATH.read_text(encoding="utf-8")
    assert not validate_pkgbuild_against_lock(load_lock(), pkgbuild)
    assert re.search(rf"(?m)^pkgver={re.escape(item['release']['version'])}$", pkgbuild)
    assert re.search(rf"(?m)^_commit='{item['commit_sha']}'$", pkgbuild)
    assert re.search(
        rf"(?m)^_archive_url='{re.escape(item['source_archive']['url'])}'$",
        pkgbuild,
    )
    assert pkgbuild.count(item["source_archive"]["sha256"]) == 1

    sabotaged = pkgbuild.replace(item["source_archive"]["sha256"], "f" * 64, 1)
    assert validate_pkgbuild_against_lock(load_lock(), sabotaged) == [
        "PKGBUILD source archive SHA-256 drift"
    ]


def test_notice_preserves_pinned_license_body_and_relationship() -> None:
    notice = NOTICE_PATH.read_text(encoding="utf-8")
    item = load_lock()["upstreams"][0]
    for value in (
        item["repository_url"],
        item["commit_sha"],
        item["license"]["source_url"],
        item["license"]["sha256"],
        "No Mnemosyne core source is copied into this repository",
        "sole authoritative L0–L5 implementation",
        "historical compatibility fixture",
    ):
        assert value in notice
    body = notice_license_body(notice).encode("utf-8")
    assert hashlib.sha256(body).hexdigest() == EXPECTED["license_sha256"]


def test_notice_full_license_validator_rejects_a_one_section_mutation() -> None:
    notice = NOTICE_PATH.read_text(encoding="utf-8")
    body = notice_license_body(notice)
    mutated = body.replace(
        "without limitation the rights",
        "without limitation ALTERED rights",
        1,
    )
    assert mutated != body
    assert hashlib.sha256(mutated.encode("utf-8")).hexdigest() != EXPECTED["license_sha256"]
