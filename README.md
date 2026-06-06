# Mnemosyne OS

**A local-first cognitive-core project that currently ships as a Python app plus an experimental Debian live ISO path. Mnemosyne is the living memory core, Tugboat is the routing layer, and an Obsidian-style graph is the primary interface.**

> Stellas Hereditabimus — we will inherit the stars.

## Current maturity (June 2026)

This repository is now a real **v0.1 runnable local scaffold**, not just a concept page.

- **Local Core (v0.1): usable for local/development workflows.** It provides a FastAPI server, JSONL memory, search, stats, graph data, Tugboat routing stub, skills store, CLI, and local dashboard.
- **ISO Distribution: experimental developer preview.** `main` builds a Debian Bookworm hybrid ISO in GitHub Actions and uploads checksumed artifacts. CI boots the ISO in QEMU and verifies `mnemosyne.service`, `/health`, and CLI search inside the VM.
- **Not production-ready yet.** There is no auth, no durable ISO persistence story, no bundled offline LLM, and no hardware USB boot certification.

What you can actually use today:

- Install and run the local cognitive core with `scripts/install-local.sh` and `scripts/run-dev.sh`.
- Store/search memories with `python bin/mnemosyne`.
- Open the local dashboard wired to `GET /memory/graph`.
- Inspect GitHub Actions artifacts from the `Build Mnemosyne OS ISO` workflow for the latest experimental ISO and checksum.

What is still future work:

- Published/release-tagged ISO download
- Hardware USB boot testing beyond QEMU
- Persistent writable memory volume in the live ISO
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
│   └── build-mnemosyne-os.sh       # Legacy Cubic/Ubuntu helper
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
- `GET /memory/stats` — memory-only counts and domains
- `GET /stats` — aggregate service stats across memory and skills
- `GET /skills`
- `POST /skills`
- `POST /tugboat/route`

## Current limitations

- Storage uses simple JSONL files; this is intentional for v0.1 but not the long-term memory backend.
- API is local-only and unauthenticated; do not bind it to a public interface.
- No bundled offline LLM yet; routing and skill distillation are still scaffold-level.
- QEMU smoke testing passes in CI, but hardware USB boot testing is still a separate gate.
- Security Guardian enforcement is not active beyond early routing/design hints.

## Distribution / live-build path

The active distribution path is Debian Bookworm userspace via live-build, not a custom kernel-first distro and not the older Cubic-first Ubuntu path. The workflow at `.github/workflows/build-iso.yml` builds the ISO on `main`, produces checksumed artifacts, and runs the QEMU smoke test automatically.

### GitHub Actions ISO build

The `Build Mnemosyne OS ISO` workflow verifies the distribution path by:

1. running the Python test suite,
2. preparing the live-build source include,
3. building `live-image-amd64.hybrid.iso` in a pinned Debian Bookworm container,
4. writing `live-image-amd64.hybrid.iso.sha256`,
5. booting the ISO in QEMU, and
6. checking `mnemosyne.service`, `curl http://127.0.0.1:8765/health`, and CLI search inside the live VM.

Artifacts are retained by GitHub Actions for short-term inspection. For a longer-lived developer-preview artifact, push a reviewed `v*` tag; the same workflow rebuilds the ISO, reruns QEMU smoke testing, and publishes the ISO plus `.sha256` to a GitHub prerelease.

### Tagged developer-preview release

Use this only after `main` is green and the README/Pages status still matches the artifact maturity:

```bash
git checkout main
git pull origin main
git tag -a v0.1.0-dev.1 -m "Mnemosyne OS v0.1.0 developer preview 1"
git push origin v0.1.0-dev.1
```

The tag workflow publishes a prerelease only after the same build, checksum, and QEMU smoke gates pass. Do not call the release production-ready until hardware USB boot testing and persistence behavior are documented.

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

### Legacy Cubic compatibility

`scripts/build-mnemosyne-os.sh` remains as a compatibility helper for old Cubic/Ubuntu experiments. New distribution work should use the Debian live-build path above.

## Security note

This is an early scaffold. Do **not** expose port `8765` to the public internet. The current API has no authentication. Treat it as local-only until the Security Guardian layer, auth, and audit controls are implemented.

## Design priorities

1. **Local-first continuity** — memory should survive sessions and devices.
2. **Inspectable cognition** — graphs, files, and skills should be visible and editable.
3. **Small shippable layers** — backend first, then dashboard, then ISO polish.
4. **Security before autonomy** — powerful tools need review, audit, and rollback.

## License

MIT. See [LICENSE](LICENSE).
