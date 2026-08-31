import copy
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "upstream" / "omarchy.lock.json"
NOTICE_PATH = ROOT / "upstream" / "NOTICE-OMARCHY.md"
ADR_PATH = ROOT / "docs" / "adr" / "0001-omarchy-compatible-substrate.md"
README_PATH = ROOT / "README.md"
EXPECTED_REPOSITORIES = {
    "omarchy": "omacom/omarchy",
    "omarchy-iso": "omacom/omarchy-iso",
    "omarchy-pkgs": "omacom/omarchy-pkgs",
}
EXPECTED_REFS = {
    "omarchy": {"kind": "tag", "name": "v4.0.1"},
    "omarchy-iso": {"kind": "branch", "name": "quattro"},
    "omarchy-pkgs": {"kind": "branch", "name": "master"},
}
EXPECTED_COMMITS = {
    "omarchy": "13f18b2cb7286fb54f87daf571a031aa6af3d8f0",
    "omarchy-iso": "d6e4060d566b41f27dd203fd014ad002f15d3616",
    "omarchy-pkgs": "8bfa0546767365ccb242034424754035e8aef364",
}
EXPECTED_UPSTREAMS = set(EXPECTED_REPOSITORIES)
EXPECTED_COPYRIGHTS = {
    "omarchy": "Copyright (c) David Heinemeier Hansson",
    "omarchy-iso": "Copyright (c) 2026 Anton Hvornum",
    "omarchy-pkgs": "Copyright (c) David Heinemeier Hansson",
}
# SHA-256 of each pinned raw LICENSE, with trailing newlines normalized to one LF.
# omarchy and omarchy-pkgs intentionally have byte-identical pinned license bodies.
EXPECTED_NOTICE_LICENSE_SHA256 = {
    "omarchy": "717ba1949502290f8e47688ae2e323acd06c8ca47aec9f7596b15f678c1af4a2",
    "omarchy-iso": "e2b1e3778a6ada6d6eee5f48c028f885e9797313f4c5705929bdc5b99db569d3",
    "omarchy-pkgs": "717ba1949502290f8e47688ae2e323acd06c8ca47aec9f7596b15f678c1af4a2",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def load_lock():
    assert LOCK_PATH.is_file(), f"missing upstream contract: {LOCK_PATH.relative_to(ROOT)}"
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def normalize_license_body(body):
    return body.rstrip("\n") + "\n"


def validate_notice_license_bodies(notice):
    errors = []
    for name, expected_digest in EXPECTED_NOTICE_LICENSE_SHA256.items():
        sections = list(
            re.finditer(
                rf"(?ms)^## {re.escape(name)}\n(?P<section>.*?)(?=^## |\Z)",
                notice,
            )
        )
        if len(sections) != 1:
            errors.append(f"{name}: expected exactly one notice section, found {len(sections)}")
            continue

        bodies = re.findall(
            r"(?ms)^```text\n(?P<body>.*?)\n```[ \t]*(?:\n|\Z)",
            sections[0].group("section"),
        )
        if len(bodies) != 1:
            errors.append(f"{name}: expected exactly one fenced license body, found {len(bodies)}")
            continue

        normalized = normalize_license_body(bodies[0]).encode("utf-8")
        if hashlib.sha256(normalized).hexdigest() != expected_digest:
            errors.append(f"{name}: license body SHA-256 mismatch")

    return errors


def validate_lock(document):
    errors = []
    required_top = {"schema", "schema_version", "retrieved_at", "pin_policy", "upstreams"}
    errors.extend(f"missing top-level field: {field}" for field in required_top - document.keys())
    if errors:
        return errors

    if document["schema"] != "mnemosyne.omarchy-upstream-lock":
        errors.append("unexpected schema")
    if document["schema_version"] != 1:
        errors.append("unexpected schema version")
    if document["retrieved_at"] != "2026-08-30":
        errors.append("unexpected retrieval date")
    if document["pin_policy"] != {
        "execution_authority": "commit_sha",
        "mutable_refs": "metadata_only",
    }:
        errors.append("commit_sha must be the sole execution authority")

    upstreams = document["upstreams"]
    if not isinstance(upstreams, list):
        return errors + ["upstreams must be a list"]
    names = {item.get("name") for item in upstreams}
    if names != EXPECTED_UPSTREAMS:
        errors.append(f"upstream set mismatch: {names!r}")
    for expected_name in EXPECTED_UPSTREAMS:
        count = sum(item.get("name") == expected_name for item in upstreams)
        if count != 1:
            errors.append(
                f"{expected_name}: expected exactly one entry, found {count}"
            )

    required_item = {
        "name",
        "repository",
        "repository_url",
        "role",
        "commit_sha",
        "ref",
        "license",
    }
    for item in upstreams:
        name = item.get("name", "<unnamed>")
        missing = required_item - item.keys()
        errors.extend(f"{name}: missing field {field}" for field in missing)
        if missing:
            continue

        sha = item["commit_sha"]
        if not isinstance(sha, str) or not SHA40.fullmatch(sha):
            errors.append(f"{name}: commit_sha is not an exact 40-hex pin")
        if sha != EXPECTED_COMMITS.get(name):
            errors.append(f"{name}: unexpected verified commit")
        if item["repository"] != EXPECTED_REPOSITORIES.get(name):
            errors.append(f"{name}: unexpected canonical repository")
        expected_url = f"https://github.com/{item['repository']}"
        if item["repository_url"] != expected_url:
            errors.append(f"{name}: repository URL is not canonical HTTPS")
        if not isinstance(item["role"], str) or not item["role"].strip():
            errors.append(f"{name}: role is empty")

        ref = item["ref"]
        if ref != EXPECTED_REFS.get(name):
            errors.append(f"{name}: human ref metadata is incomplete or unexpected")

        license_record = item["license"]
        if not isinstance(license_record, dict):
            errors.append(f"{name}: license record is invalid")
            continue
        if license_record.get("spdx_id") != "MIT":
            errors.append(f"{name}: license is not MIT")
        source_path = license_record.get("source_path")
        if not source_path:
            errors.append(f"{name}: license source path is missing")
        expected_license_url = f"{expected_url}/blob/{sha}/{source_path}"
        if license_record.get("source_url") != expected_license_url:
            errors.append(f"{name}: license source URL is not commit-pinned")

    return errors


def test_lock_is_valid_deterministic_json():
    document = load_lock()
    assert not validate_lock(document), validate_lock(document)
    serialized = json.dumps(document, indent=2, sort_keys=True) + "\n"
    assert LOCK_PATH.read_text(encoding="utf-8") == serialized


def test_validator_rejects_missing_repository_and_fields():
    document = load_lock()
    missing_repo = copy.deepcopy(document)
    missing_repo["upstreams"] = missing_repo["upstreams"][:-1]
    assert any("upstream set mismatch" in error for error in validate_lock(missing_repo))

    missing_field = copy.deepcopy(document)
    missing_field["upstreams"][0].pop("role")
    assert any("missing field role" in error for error in validate_lock(missing_field))


def test_validator_rejects_duplicate_upstream_entry():
    document = load_lock()
    duplicated = copy.deepcopy(document)
    duplicated["upstreams"].append(copy.deepcopy(duplicated["upstreams"][0]))

    assert any("exactly one entry" in error for error in validate_lock(duplicated))


def test_validator_rejects_malformed_or_mutable_only_pins():
    document = load_lock()
    malformed = copy.deepcopy(document)
    malformed["upstreams"][0]["commit_sha"] = "quattro"
    assert any("exact 40-hex pin" in error for error in validate_lock(malformed))

    mutable_only = copy.deepcopy(document)
    mutable_only["upstreams"][0].pop("commit_sha")
    assert any("missing field commit_sha" in error for error in validate_lock(mutable_only))


def test_validator_rejects_coherent_but_unverified_commit_mutation():
    document = load_lock()
    mutated = copy.deepcopy(document)
    upstream = mutated["upstreams"][0]
    replacement_sha = "0" * 40
    upstream["commit_sha"] = replacement_sha
    upstream["license"]["source_url"] = (
        f"{upstream['repository_url']}/blob/{replacement_sha}/"
        f"{upstream['license']['source_path']}"
    )

    assert any("unexpected verified commit" in error for error in validate_lock(mutated))


def test_validator_rejects_non_mit_or_unpinned_license_sources():
    document = load_lock()
    wrong_license = copy.deepcopy(document)
    wrong_license["upstreams"][0]["license"]["spdx_id"] = "NOASSERTION"
    assert any("license is not MIT" in error for error in validate_lock(wrong_license))

    mutable_license = copy.deepcopy(document)
    mutable_license["upstreams"][0]["license"]["source_url"] = (
        "https://github.com/omacom/omarchy/blob/quattro/LICENSE"
    )
    assert any("license source URL is not commit-pinned" in error for error in validate_lock(mutable_license))


def test_notice_tracks_every_lock_and_preserves_mit_attribution():
    document = load_lock()
    assert NOTICE_PATH.is_file(), f"missing notice: {NOTICE_PATH.relative_to(ROOT)}"
    notice = NOTICE_PATH.read_text(encoding="utf-8")
    for item in document["upstreams"]:
        name = item["name"]
        assert f"## {name}\n" in notice
        assert item["repository_url"] in notice
        assert item["commit_sha"] in notice
        assert item["license"]["source_url"] in notice
        assert EXPECTED_COPYRIGHTS[name] in notice
    assert notice.count("Permission is hereby granted, free of charge") == 3
    assert notice.count('THE SOFTWARE IS PROVIDED "AS IS"') == 3
    assert "No Omarchy source is copied by this PR" in notice
    assert "copied or substantially derived" in notice
    assert "preserve the applicable upstream notice" in notice


def test_notice_preserves_each_pinned_mit_license_body_exactly_offline():
    notice = NOTICE_PATH.read_text(encoding="utf-8")

    assert not validate_notice_license_bodies(notice)


def test_notice_exact_body_validator_rejects_only_the_mutated_named_section():
    notice = NOTICE_PATH.read_text(encoding="utf-8")
    section_start = notice.index("## omarchy\n")
    section_end = notice.index("## omarchy-iso\n")
    omarchy_section = notice[section_start:section_end]
    mutated_section = omarchy_section.replace(
        "without limitation the rights",
        "without limitation ALTERED rights",
        1,
    )
    assert mutated_section != omarchy_section
    mutated_notice = notice[:section_start] + mutated_section + notice[section_end:]

    assert validate_notice_license_bodies(mutated_notice) == [
        "omarchy: license body SHA-256 mismatch"
    ]


def test_adr_records_substrate_decision_and_safety_invariants():
    assert ADR_PATH.is_file(), f"missing ADR: {ADR_PATH.relative_to(ROOT)}"
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    required_phrases = (
        "distro-independent",
        "portable service/package",
        "thin, optional adapter",
        "owned iso is last",
        "historical fixture",
        "source merger",
        "full fork",
        "atxgreene/mnemosyne",
        "reversible packages",
        "snapshots do not replace icms backups",
    )
    for phrase in required_phrases:
        assert phrase in adr, phrase
    assert "upstream/omarchy.lock.json" in adr
    assert "upstream/notice-omarchy.md" in adr


def test_adr_limits_jsonl_to_temporary_import_compatibility():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert (
        "jsonl is a temporary compatibility/import-only surface, not a second cognitive core."
        in adr
    )


def test_adr_scopes_one_core_contract_to_target_and_qualifies_bundled_v01():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    for sentence in (
        "under the target architecture, `atxgreene/mnemosyne` is the sole authoritative "
        "cognitive implementation.",
        "this repository's currently bundled `mnemosyne/` jsonl v0.1 implementation "
        "remains a historical developer-preview compatibility fixture pending migration "
        "to the authoritative core.",
        "its current runnable behavior is documented honestly, but it must not accrue "
        "competing long-term memory, policy, or cognition semantics.",
        "jsonl is temporary compatibility/import infrastructure in the target architecture.",
    ):
        assert sentence in adr, sentence


def test_adr_keeps_service_loopback_same_origin_pending_reviewed_auth_model():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert (
        "the service remains loopback-only and same-origin until a separately reviewed "
        "authentication and authorization threat model exists."
        in adr
    )


def test_adr_denies_privilege_authority_to_every_agent_output_path():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert (
        "no memory, model, shell plugin, or ai agent output may directly authorize "
        "privileged commands."
        in adr
    )


def test_adr_does_not_inherit_omarchy_agent_bypass_defaults():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert (
        "omarchy agent auto-approval or permission-bypass defaults must not be inherited."
        in adr
    )


def test_adr_defers_the_first_generic_linux_arch_service_layer_until_after_contracts():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert (
        "after the phase 0 contracts, the first implementation layer will be a generic "
        "linux/arch package plus a hardened systemd user service."
        in adr
    )
    assert (
        "that layer is future implementation work, not something delivered by this phase "
        "0.1 pr."
        in adr
    )


def test_adr_keeps_the_full_reversible_package_lifecycle_explicit():
    adr = ADR_PATH.read_text(encoding="utf-8").lower()
    assert "reversible packages" in adr
    assert "explicit install, upgrade, rollback, and removal boundaries" in adr


def test_readme_tracks_current_and_future_distribution_maturity_without_drift():
    readme = README_PATH.read_text(encoding="utf-8").lower()
    assert "| track | maturity | scope |" in readme
    for phrase in (
        "debian developer-preview fixture",
        "portable service/package",
        "optional omarchy adapter",
        "thin owned image",
        "historical",
        "future",
        "eventual",
    ):
        assert phrase in readme, phrase
    for path in (
        "docs/adr/0001-omarchy-compatible-substrate.md",
        "upstream/omarchy.lock.json",
        "upstream/notice-omarchy.md",
    ):
        assert path in readme


def test_readme_distinguishes_runnable_bundled_fixture_from_target_core():
    readme = README_PATH.read_text(encoding="utf-8").lower()
    for sentence in (
        "under the target architecture, `atxgreene/mnemosyne` is the sole authoritative "
        "cognitive implementation.",
        "the bundled `mnemosyne/` jsonl v0.1 implementation remains runnable today as a "
        "historical developer-preview compatibility fixture pending migration to that "
        "authoritative core.",
        "it is not the target authoritative core or a second long-term cognitive "
        "implementation, and it must not accrue competing long-term memory, policy, or "
        "cognition semantics.",
        "jsonl is active storage for this runnable v0.1 fixture, but it is temporary "
        "compatibility/import infrastructure in the target architecture.",
    ):
        assert sentence in readme, sentence
