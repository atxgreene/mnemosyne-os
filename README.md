# Mnemosyne OS

**A local-first cognitive operating-system scaffold with Mnemosyne as the living memory core, Tugboat as the routing layer, and an Obsidian-style memory graph as the primary interface.**

> Stellas Hereditabimus — we will inherit the stars.

## Current status

This repository is now a real **v0.1 runnable scaffold**, not just a concept page.

What works today:

- Local JSONL memory store
- Memory search
- Live memory graph endpoint
- Starter skills store
- Tugboat routing stub
- FastAPI cognitive-core server
- Native `mnemosyne` CLI helper
- Local dashboard that talks to the API
- Starter memory + starter skills seed files
- GitHub Pages concept/demo site
- Cubic-oriented Ubuntu service install script
- OS packaging foundation with systemd installer
- live-build ISO scaffold for a flashable Linux developer preview
- GitHub Actions ISO build workflow on `main`
- Checksum-verified Debian Bookworm live ISO artifact
- CI QEMU smoke test that verifies boot, `mnemosyne.service`, `/health`, and CLI search inside the live VM
- Explicit source-on-OS target at `/opt/mnemosyne-os/source`

What is still future work:

- Published/release-tagged ISO download
- Hardware USB boot testing beyond QEMU
- Real vector store backend
- LLM-powered skill distillation
- Profile isolation
- Security Guardian enforcement beyond routing hints
- Offline local model bundle
- Plymouth/GRUB visual theming package

## Repository structure

```text
mnemosyne-os/
├── assets/                         # Demo GIF and visual assets
├── bin/mnemosyne                   # Native CLI helper
├── dashboard/mnemosyne-panels.html # Local live dashboard
├── docs/
│   ├── index.html                  # GitHub Pages site
│   └── plans/                      # Implementation roadmaps
├── iso/                            # live-build scaffold + ISO test docs
├── kernel/                         # custom-kernel track docs/placeholders
├── mnemosyne/
│   ├── core/memory.py              # Local memory store + graph builder
│   ├── services/api_server.py      # FastAPI server
│   ├── skills/store.py             # Starter skill store
│   └── tugboat/router.py           # Declarative routing stub
├── packaging/                      # installer + systemd unit for OS image
├── scripts/
│   ├── install-local.sh            # Local dev installer
│   ├── prepare-live-build.sh       # Copies repo source into live-build tree
│   ├── run-dev.sh                  # Start API server
│   ├── load-starter-content.py     # Seed memory + skills
│   └── build-mnemosyne-os.sh       # Cubic/Ubuntu install scaffold
├── seed/                           # Starter memories and skills
├── tests/                          # Pytest suite
├── LICENSE
└── PHILOSOPHY.md
```

## Quick start

```bash
git clone https://github.com/atxgreene/mnemosyne-os.git
cd mnemosyne-os
./scripts/install-local.sh
./scripts/run-dev.sh
```

Then open:

```text
http://127.0.0.1:8765/docs
```

Or open the local dashboard file:

```text
dashboard/mnemosyne-panels.html
```

## CLI examples

```bash
python bin/mnemosyne store "Memory graphs help make continuity visible" --domain memory-graph --importance high
python bin/mnemosyne search "memory graph" --json
python bin/mnemosyne route "Synthesize research on cognitive OS design" --json
python bin/mnemosyne graph --json
python bin/mnemosyne dashboard
```

## API endpoints

- `GET /health`
- `POST /memory/add`
- `GET /memory/search?query=...`
- `GET /memory/graph`
- `GET /memory/stats`
- `GET /stats`
- `GET /skills`
- `POST /skills`
- `POST /tugboat/route`

## Current limitations

- Storage uses simple JSONL files; this is intentional for v0.1 but not the long-term memory backend.
- API is local-only and unauthenticated; do not bind it to a public interface.
- No bundled offline LLM yet; routing and skill distillation are still scaffold-level.
- QEMU smoke testing passes in CI, but hardware USB boot testing is still a separate gate.
- Security Guardian enforcement is not active beyond early routing/design hints.

## Custom Linux / live-build path

The practical path toward a true Mnemosyne OS ISO is Debian userspace first, not a custom kernel first. The current live-build config pins Debian Bookworm because Ubuntu-mode live-build on current runners tried to pull obsolete syslinux/gfxboot theme packages.

### Local OS installer

On a Debian/Ubuntu VM or chroot, install the repo into the OS image with:

```bash
sudo ./packaging/install-mnemosyne-os.sh --source "$PWD"
```

That installer:

- copies the full repository source to `/opt/mnemosyne-os/source`
- creates a virtualenv at `/opt/mnemosyne-os/.venv`
- seeds starter memory/skills into `/var/lib/mnemosyne`
- installs `/usr/local/bin/mnemosyne`
- installs and enables `mnemosyne.service`
- keeps the API bound to `127.0.0.1:8765`

### live-build ISO scaffold

The ISO scaffold lives under `iso/live-build/`. On a Linux build host:

```bash
./scripts/prepare-live-build.sh
cd iso/live-build
sudo lb clean --purge || true
sudo bash auto/config
sudo lb build
sha256sum live-image-amd64.hybrid.iso > live-image-amd64.hybrid.iso.sha256
```

Then follow `iso/README.md` for QEMU smoke testing and flash guidance.

### Cubic compatibility

Inside a Cubic chroot, after copying this repo to `/opt/mnemosyne-os/source`, run:

```bash
cd /opt/mnemosyne-os/source
sudo ./scripts/build-mnemosyne-os.sh
```

## Security note

This is an early scaffold. Do **not** expose port `8765` to the public internet. The current API has no authentication. Treat it as local-only until the Security Guardian layer, auth, and audit controls are implemented.

## Design priorities

1. **Local-first continuity** — memory should survive sessions and devices.
2. **Inspectable cognition** — graphs, files, and skills should be visible and editable.
3. **Small shippable layers** — backend first, then dashboard, then ISO polish.
4. **Security before autonomy** — powerful tools need review, audit, and rollback.

## License

MIT. See [LICENSE](LICENSE).
