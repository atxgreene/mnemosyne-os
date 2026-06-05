from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-iso.yml"


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
        "./scripts/prepare-live-build.sh",
        "sudo lb clean --purge || true",
        "sudo lb config",
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
