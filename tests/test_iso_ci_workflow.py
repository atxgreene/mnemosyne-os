from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-iso.yml"


def test_live_build_auto_config_pins_supported_ubuntu_release():
    auto_config = ROOT / "iso" / "live-build" / "auto" / "config"
    assert auto_config.exists()
    text = auto_config.read_text(encoding="utf-8")
    for required in [
        "--mode ubuntu",
        "--distribution noble",
        "--archive-areas \"main universe\"",
        "--binary-images iso-hybrid",
        "--debian-installer false",
    ]:
        assert required in text


def test_iso_build_workflow_exists_and_installs_live_build_toolchain():
    assert WORKFLOW.exists(), "GitHub Actions ISO build workflow should exist"
    text = WORKFLOW.read_text(encoding="utf-8")
    for required in [
        "live-build",
        "qemu-system-x86",
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
        "sudo lb clean --purge || true",
        "sudo bash auto/config",
        "sudo lb build",
        "sha256sum live-image-amd64.hybrid.iso",
        "actions/upload-artifact",
        "live-image-amd64.hybrid.iso",
        "live-image-amd64.hybrid.iso.sha256",
    ]:
        assert required in text


def test_iso_build_workflow_runs_existing_test_suite_first():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "python -m pytest tests -q" in text
