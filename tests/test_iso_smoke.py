from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_iso_smoke_systemd_unit_and_script_are_packaged():
    service = ROOT / "packaging" / "systemd" / "mnemosyne-iso-smoke.service"
    script = ROOT / "packaging" / "smoke" / "mnemosyne-iso-smoke.sh"
    install = (ROOT / "packaging" / "install-mnemosyne-os.sh").read_text(encoding="utf-8")

    assert service.exists()
    assert script.exists()
    smoke_text = script.read_text(encoding="utf-8")
    assert "MARKER_PREFIX=MNEMOSYNE_ISO_SMOKE" in smoke_text
    assert 'emit "PASS"' in smoke_text
    assert "mnemosyne-iso-smoke.service" in install
    assert "systemctl enable mnemosyne-iso-smoke.service" in install


def test_qemu_smoke_script_waits_for_guest_pass_marker():
    script = ROOT / "scripts" / "smoke-test-iso-qemu.sh"
    text = script.read_text(encoding="utf-8")
    for required in [
        "qemu-system-x86_64",
        "-serial file:",
        "MNEMOSYNE_ISO_SMOKE: PASS",
        "MNEMOSYNE_ISO_SMOKE: FAIL",
    ]:
        assert required in text
