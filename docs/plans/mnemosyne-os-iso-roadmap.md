# Mnemosyne OS Flashable ISO Roadmap

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Produce a testable, flashable Linux ISO that boots into a local-first Mnemosyne OS userspace with source code, CLI, API service, dashboard, seed data, and local docs included on disk.

**Architecture:** Start with a Debian/Ubuntu live-build derivative rather than a custom kernel-first distro. Mnemosyne lives in userspace under `/opt/mnemosyne-os/source`, persistent/runtime data lives under `/var/lib/mnemosyne`, and the local API is managed by systemd. Custom kernel work becomes a later track once the bootable userspace artifact is real.

**Tech Stack:** Debian/Ubuntu live-build, systemd, Python 3.11+, FastAPI/Uvicorn, local JSONL/JSON stores, QEMU for VM smoke testing.

---

## Target artifact

A testable ISO image that can be booted in a VM and, after validation, written to USB as a flashable developer preview.

The ISO must include:

- Full repository source code at `/opt/mnemosyne-os/source`
- Python virtual environment at `/opt/mnemosyne-os/.venv`
- Runtime memory/skills home at `/var/lib/mnemosyne`
- CLI symlink/launcher at `/usr/local/bin/mnemosyne`
- Systemd service `mnemosyne.service`
- Local API bound to `127.0.0.1:8765`
- Dashboard source available under `/opt/mnemosyne-os/source/dashboard/`
- Seed memories and skills loaded on first build/install
- Build/flash/test docs checked into the repo

## Release gates

### Gate 1 — Repo scaffold ready

- `iso/README.md` explains build, VM test, checksum, and flash flow.
- `iso/live-build/config/` contains a minimal live-build config scaffold.
- `packaging/install-mnemosyne-os.sh` can install from a repo checkout into `/opt/mnemosyne-os/source`.
- `packaging/systemd/mnemosyne.service` runs the local API from packaged source.
- Tests verify the scaffold files and required paths exist.

### Gate 2 — Local installer test

Run on a clean Ubuntu/Debian VM or chroot:

```bash
sudo ./packaging/install-mnemosyne-os.sh --source "$PWD"
systemctl status mnemosyne --no-pager
curl http://127.0.0.1:8765/health
mnemosyne route "Deploy safely with security review" --json
```

Expected:

- `mnemosyne.service` is active or starts cleanly.
- `/health` returns `ok: true`.
- CLI resolves from `/usr/local/bin/mnemosyne`.
- Starter memory count is non-zero.

### Gate 3 — ISO build test

From a Debian/Ubuntu build host with live-build installed:

```bash
cd iso/live-build
sudo lb clean --purge || true
sudo lb config
sudo lb build
sha256sum live-image-amd64.hybrid.iso > live-image-amd64.hybrid.iso.sha256
```

Expected:

- ISO file exists.
- SHA256 file exists.
- Build logs contain the Mnemosyne install hook.

### Gate 4 — VM boot smoke test

```bash
qemu-system-x86_64 \
  -m 4096 \
  -smp 2 \
  -cdrom iso/live-build/live-image-amd64.hybrid.iso \
  -boot d \
  -enable-kvm
```

Inside the VM:

```bash
systemctl status mnemosyne --no-pager
curl http://127.0.0.1:8765/health
mnemosyne search Mnemosyne --json
ls /opt/mnemosyne-os/source
```

Expected:

- Mnemosyne source code is present on the OS.
- API and CLI work locally.
- Service binds only to localhost.

### Gate 5 — Flashable developer preview

Flash only after VM boot smoke test passes and the checksum is recorded.

Example Linux flow:

```bash
sha256sum -c live-image-amd64.hybrid.iso.sha256
sudo dd if=live-image-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress conv=fsync
```

Replace `/dev/sdX` carefully. Wrong target destroys data.

## Custom kernel track

Do not block the v0.2 ISO on custom kernel work. The first real custom kernel milestone should be:

1. Document base kernel version from the chosen distro.
2. Add a `kernel/README.md` with config goals and non-goals.
3. Add a config fragment only after the live ISO boots reliably.
4. Build a kernel package separately from the userspace ISO.
5. Add VM boot verification before any flash guidance.

Initial custom kernel goals should be boring and auditable:

- stable hardware support
- secure defaults
- local-first networking posture
- no exposed Mnemosyne API ports
- reproducible config fragments

## Not in scope for first testable ISO

- From-scratch distro
- Kernel patches
- Full disk persistence
- LLM bundle preinstallation
- Secure multi-user auth
- Public network API exposure

## Ready-for-testing definition

This branch is ready for Austin to test when:

- Tests pass locally.
- The install script is executable.
- The live-build hook references the installer and source path.
- README and `iso/README.md` explain exact test commands.
- Branch is pushed to GitHub for review or VM build on Linux.
