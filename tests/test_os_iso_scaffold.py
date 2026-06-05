from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_os_iso_roadmap_names_flashable_artifacts():
    roadmap = read("docs/plans/mnemosyne-os-iso-roadmap.md")
    assert "flashable" in roadmap.lower()
    assert "/opt/mnemosyne-os/source" in roadmap
    assert "VM boot smoke test" in roadmap
    assert "custom kernel" in roadmap.lower()


def test_systemd_service_runs_local_api_from_packaged_source():
    service = read("packaging/systemd/mnemosyne.service")
    assert "WorkingDirectory=/opt/mnemosyne-os/source" in service
    assert "MNEMOSYNE_HOME=/var/lib/mnemosyne" in service
    assert "127.0.0.1" in service
    assert "8765" in service


def test_packaging_installer_copies_source_and_installs_cli():
    installer = read("packaging/install-mnemosyne-os.sh")
    assert "SOURCE_DIR=/opt/mnemosyne-os/source" in installer
    assert "rsync" in installer
    assert "/usr/local/bin/mnemosyne" in installer
    assert "load-starter-content.py" in installer
    assert "mnemosyne.service" in installer
    assert "skipping self-rsync" in installer


def test_prepare_live_build_excludes_generated_include_tree():
    prepare = read("scripts/prepare-live-build.sh")
    assert "config/includes.chroot/opt/mnemosyne-os/source" in prepare
    assert "--exclude 'iso/live-build/config/includes.chroot/'" in prepare


def test_live_build_hooks_include_source_and_service():
    hook = read("iso/live-build/config/hooks/normal/010-install-mnemosyne.hook.chroot")
    package_list = read("iso/live-build/config/package-lists/mnemosyne.list.chroot")
    assert "/opt/mnemosyne-os/source" in hook
    assert "install-mnemosyne-os.sh" in hook
    assert "mnemosyne.service" in hook
    assert "live-build" in package_list
    assert "python3-venv" in package_list


def test_iso_readme_has_build_and_flash_testing_commands():
    readme = read("iso/README.md")
    assert "lb build" in readme
    assert "qemu-system-x86_64" in readme
    assert "sha256sum" in readme
    assert "Flash only after" in readme
