from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-iso.yml"


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
        "--security false",
        "--linux-packages linux-image",
    ]:
        assert required in text


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


def test_iso_build_workflow_can_publish_tagged_developer_preview_release():
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in [
        "pull_request:",
        "branches:",
        "tags:",
        "- 'v*'",
        "permissions:",
        "contents: write",
        "Publish tagged developer-preview release",
        "startsWith(github.ref, 'refs/tags/v')",
        "gh release create",
        "--prerelease",
        "live-image-amd64.hybrid.iso.sha256",
    ]:
        assert required in text
