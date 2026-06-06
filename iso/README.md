# Mnemosyne OS ISO Foundation

This directory contains the active live-build scaffold for producing the experimental Mnemosyne OS Debian developer-preview ISO.

The current goal is a **testable userspace ISO**, not a custom-kernel distro yet. The ISO should boot a standard Debian live environment and install Mnemosyne source, service, CLI, dashboard, and seed data onto the image.

## Build host requirements

Use a Debian/Ubuntu machine or VM. Windows/Git Bash is fine for repo editing, but actual ISO builds should run on Linux. The checked-in `auto/config` currently pins Debian Bookworm for reproducible live-build output.

```bash
sudo apt-get update
sudo apt-get install -y live-build qemu-system-x86 xorriso isolinux syslinux-utils squashfs-tools
```

## Build

```bash
cd iso/live-build
sudo lb clean --purge || true
sudo bash auto/config
sudo lb build
sha256sum live-image-amd64.hybrid.iso > live-image-amd64.hybrid.iso.sha256
```

Expected outputs:

```text
iso/live-build/live-image-amd64.hybrid.iso
iso/live-build/live-image-amd64.hybrid.iso.sha256
```

## VM boot smoke test

```bash
qemu-system-x86_64 \
  -m 4096 \
  -smp 2 \
  -cdrom iso/live-build/live-image-amd64.hybrid.iso \
  -boot d
```

If KVM is available on Linux, add:

```bash
-enable-kvm
```

Inside the VM, verify:

```bash
systemctl status mnemosyne --no-pager
curl http://127.0.0.1:8765/health
mnemosyne search Mnemosyne --json
mnemosyne route "Deploy safely with security review" --json
ls /opt/mnemosyne-os/source
```

Expected:

- `/opt/mnemosyne-os/source` contains the repo source code.
- `/usr/local/bin/mnemosyne` runs the CLI.
- `mnemosyne.service` starts the FastAPI server.
- API binds to `127.0.0.1:8765`, not a public interface.

## CI smoke-test evidence

On `main`, the `Build Mnemosyne OS ISO` GitHub Actions workflow builds the ISO, uploads `live-image-amd64.hybrid.iso` plus its `.sha256`, boots the ISO in QEMU, and verifies:

- `mnemosyne.service` is active,
- `curl http://127.0.0.1:8765/health` responds,
- `mnemosyne search Mnemosyne --json` works inside the live VM.

Manual QEMU testing is still useful before flashing hardware, but the basic VM smoke gate now runs automatically in CI.

## Flashing

Flash only after the VM boot smoke test passes and the checksum is recorded.

```bash
sha256sum -c live-image-amd64.hybrid.iso.sha256
lsblk
sudo dd if=live-image-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

Replace `/dev/sdX` with the actual USB device. This is destructive.

## Current limitations

- The CI workflow produces a QEMU-verified ISO artifact, but there is no long-lived release artifact yet.
- Persistence is not configured yet; live-session memories may be ephemeral unless the deployment provides a writable volume.
- No custom kernel is built yet.
- No bundled local LLM is included yet.
- API auth is not implemented; keep the service localhost-only.

## Next testing milestone

Promote a green CI artifact into a tagged developer-preview release, then perform hardware USB boot testing and document persistence behavior across reboots.
