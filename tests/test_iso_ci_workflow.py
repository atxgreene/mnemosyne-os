from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-iso.yml"


def workflow_event_paths(text, event):
    match = re.search(
        rf"(?ms)^  {re.escape(event)}:\n.*?^    paths:\n(?P<paths>(?:^      - [^\n]+\n)+)",
        text,
    )
    assert match, f"missing {event} path filters"
    return {
        line.removeprefix("- ").strip("'\"")
        for line in map(str.strip, match.group("paths").splitlines())
    }


def test_live_build_auto_config_pins_supported_debian_release():
    auto_config = ROOT / "iso" / "live-build" / "auto" / "config"
    assert auto_config.exists()
    text = auto_config.read_text(encoding="utf-8")
    for required in [
        "--mode debian",
        "--distribution bookworm",
        "--archive-areas \"main contrib non-free-firmware\"",
        "--binary-images iso-hybrid",
        "--debian-installer false",
        "--linux-packages linux-image",
    ]:
        assert required in text
    assert "--security false" not in text, "Debian security updates must remain enabled"


def test_iso_build_workflow_exists_and_builds_inside_debian_container():
    assert WORKFLOW.exists(), "GitHub Actions ISO build workflow should exist"
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in [
        "docker run --privileged --rm",
        "debian:bookworm",
        "live-build",
        "xorriso",
        "isolinux",
        "syslinux-utils",
        "squashfs-tools",
    ]:
        assert required in text
    assert re.search(
        r"debian:bookworm-[0-9]+@sha256:[0-9a-f]{64}",
        text,
    ), "the Debian build container must remain pinned by an immutable digest"


def test_iso_build_workflow_prepares_builds_hashes_and_uploads_iso():
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in [
        "bash ./scripts/prepare-live-build.sh",
        "qemu-system-x86 xorriso",
        "MNEMOSYNE_QEMU_TIMEOUT_SECONDS=1200 bash ./scripts/smoke-test-iso-qemu.sh",
        "mnemosyne-qemu-smoke-serial-log",
        "lb clean --purge || true",
        "bash auto/config",
        "lb build",
        "sha256sum live-image-amd64.hybrid.iso",
        "actions/upload-artifact",
        "live-image-amd64.hybrid.iso",
        "live-image-amd64.hybrid.iso.sha256",
    ]:
        assert required in text


def test_iso_build_workflow_runs_existing_test_suite_first():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python -m pytest tests -q" in text


def test_iso_build_workflow_runs_for_contract_only_changes():
    text = WORKFLOW.read_text(encoding="utf-8")
    required_contract_paths = {"docs/adr/**", "upstream/**", "pyproject.toml"}

    for event in ("pull_request", "push"):
        paths = workflow_event_paths(text, event)
        assert required_contract_paths <= paths, (
            f"{event} must trigger ISO CI for contract-only changes; "
            f"missing {required_contract_paths - paths}"
        )


def test_iso_build_workflow_can_publish_tagged_developer_preview_release():
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in [
        "pull_request:",
        "branches:",
        "tags:",
        "- 'v*'",
        "permissions:",
        "contents: read",
        "publish-release:",
        "contents: write",
        "Publish tagged developer-preview release",
        "startsWith(github.ref, 'refs/tags/v')",
        "gh release create",
        "--prerelease",
        "live-image-amd64.hybrid.iso.sha256",
    ]:
        assert required in text


def test_iso_build_workflow_uses_hashed_dependencies_and_immutable_actions():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pip install --require-hashes -r requirements.txt" in text
    action_refs = re.findall(r"uses:\s+[^\s@]+@([^\s#]+)", text)
    assert action_refs
    assert all(re.fullmatch(r"[0-9a-f]{40}", ref) for ref in action_refs), action_refs


def test_iso_build_workflow_generates_sbom_and_attests_tagged_artifacts():
    text = WORKFLOW.read_text(encoding="utf-8")
    build_block, release_and_attest = text.split("  publish-release:", 1)
    release_block, attest_block = release_and_attest.split("  attest-release:", 1)

    assert "generate-python-sbom.py" in build_block
    assert "mnemosyne-python-sbom.cdx.json" in build_block

    assert "startsWith(github.ref, 'refs/tags/v')" in release_block
    assert "mnemosyne-python-sbom.cdx.json" in release_block

    assert "startsWith(github.ref, 'refs/tags/v')" in attest_block
    assert "attest-build-provenance" in attest_block
    assert "id-token: write" in attest_block
    assert "attestations: write" in attest_block
    assert "subject-path: 'release-artifacts/*'" in attest_block

    for elevated_permission in ("id-token: write", "attestations: write"):
        assert elevated_permission not in build_block
        assert elevated_permission not in release_block


def test_release_write_permission_is_not_granted_to_build_job():
    text = WORKFLOW.read_text(encoding="utf-8")
    build_block, release_block = text.split("  publish-release:", 1)
    assert "contents: write" not in build_block
    assert "contents: write" in release_block
