# Mnemosyne OS

**A local-first cognitive-core project that currently ships as a Python app plus an experimental Debian live ISO path. Mnemosyne is the living memory core, Tugboat is the routing layer, and an Obsidian-style graph is the primary interface.**

> Stellas Hereditabimus — we will inherit the stars.

## Current maturity (August 2026)

This repository is now a real **v0.1 runnable local scaffold**, not just a concept page.

| Track | Maturity | Scope |
| --- | --- | --- |
| Debian developer-preview fixture | Maintained historical v0.1 fixture | Existing live-build/QEMU regression path; not the future substrate architecture. |
| Portable service/package | Future — first substrate deliverable | Distro-independent packaging for the single Mnemosyne cognitive core. |
| Optional Omarchy adapter | Future — after portable packaging | Thin, removable integration; not an Omarchy source merger or fork. |
| Thin owned image | Eventual — last | Downstream image assembly only after package and adapter contracts are proven. |

Phase 0.1 records the substrate decision in [`docs/adr/0001-omarchy-compatible-substrate.md`](docs/adr/0001-omarchy-compatible-substrate.md), immutable upstream provenance in [`upstream/omarchy.lock.json`](upstream/omarchy.lock.json), and applicable MIT notices in [`upstream/NOTICE-OMARCHY.md`](upstream/NOTICE-OMARCHY.md). These are contracts only; they do not implement the future package, adapter, or image.

Under the target architecture, `atxgreene/Mnemosyne` is the sole authoritative cognitive implementation. The bundled `mnemosyne/` JSONL v0.1 implementation remains runnable today as a historical developer-preview compatibility fixture pending migration to that authoritative core. It is not the target authoritative core or a second long-term cognitive implementation, and it must not accrue competing long-term memory, policy, or cognition semantics.

- **Bundled v0.1 fixture: usable for local/development workflows today.** It provides a FastAPI server, JSONL memory, search, stats, graph data, Tugboat routing stub, skills store, CLI, and local dashboard.
- **ISO Distribution: experimental developer preview.** `main` builds a Debian Bookworm hybrid ISO in GitHub Actions and uploads checksumed artifacts. CI boots the ISO in QEMU and verifies `mnemosyne.service`, `/health`, and CLI search inside the VM.
- **Not production-ready yet.** There is no auth, no durable ISO persistence story, no bundled offline LLM, and no hardware USB boot certification.

What you can actually use today:

- Install and run the bundled v0.1 developer-preview fixture with `scripts/install-local.sh` and `scripts/run-dev.sh`.
- Store/search memories with `python bin/mnemosyne`.
- Open the loopback-served dashboard wired to `GET /memory/graph`.
- Inspect GitHub Actions artifacts from the `Build Mnemosyne OS ISO` workflow for the latest experimental ISO, checksum, and Python CycloneDX SBOM.

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

Python 3.11+ is required. The local and OS installers fail fast if the selected interpreter—or an existing virtual environment—uses an older Python, before installing locked dependencies. By default they select `python3`; set `MNEMOSYNE_PYTHON=/path/to/python3.11` to choose another interpreter.

```bash
git clone https://github.com/atxgreene/mnemosyne-os.git
cd mnemosyne-os
./scripts/install-local.sh
./scripts/run-dev.sh
```

Then open the dashboard or API docs:

```text
http://127.0.0.1:8765/dashboard
http://127.0.0.1:8765/docs
```

The dashboard is intentionally served by the loopback API rather than opened as a `file://` page. You can also launch it with:

```bash
python bin/mnemosyne dashboard
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

- `GET /dashboard` — loopback-served local dashboard
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

- JSONL is active storage for this runnable v0.1 fixture, but it is temporary compatibility/import infrastructure in the target architecture.
- API is local-only and unauthenticated; do not bind it to a public interface.
- No bundled offline LLM yet; routing and skill distillation are still scaffold-level.
- QEMU smoke testing passes in CI, but hardware USB boot testing is still a separate gate.
- Security Guardian enforcement is not active beyond early routing/design hints.

## Distribution / live-build path

The maintained Debian v0.1 distribution fixture uses Bookworm userspace via live-build, not a custom kernel-first distro and not the older Cubic-first Ubuntu path. The workflow at `.github/workflows/build-iso.yml` builds the ISO on `main`, produces checksumed artifacts, and runs the QEMU smoke test automatically.

### GitHub Actions ISO build

The `Build Mnemosyne OS ISO` workflow verifies the distribution path by:

1. installing the fully pinned Python dependency graph with required SHA-256 hashes,
2. running the Python test suite,
3. preparing the live-build source include,
4. generating `mnemosyne-python-sbom.cdx.json`,
5. building `live-image-amd64.hybrid.iso` in a digest-pinned Debian Bookworm container with Debian security updates enabled,
6. writing `live-image-amd64.hybrid.iso.sha256`,
7. booting the ISO in QEMU, and
8. checking `mnemosyne.service`, `curl http://127.0.0.1:8765/health`, and CLI search inside the live VM.

Artifacts are retained by GitHub Actions for short-term inspection. For a longer-lived developer-preview artifact, push a reviewed `v*` tag; the same workflow rebuilds the ISO, reruns QEMU smoke testing, publishes the ISO, checksum, and Python SBOM to a GitHub prerelease, and records GitHub artifact provenance attestations.

### Dependency lock maintenance

`requirements.in` contains the direct Python dependencies. `requirements.txt` is the reviewed, hash-locked transitive graph used by local installers, image installation, and CI. Regenerate it deliberately with Python 3.11 and pip-tools 7.5.3:

```bash
python3.11 -m venv /tmp/mnemosyne-lock
/tmp/mnemosyne-lock/bin/pip install pip-tools==7.5.3
/tmp/mnemosyne-lock/bin/pip-compile --generate-hashes --strip-extras --output-file requirements.txt requirements.in
python3.11 -m venv /tmp/mnemosyne-lock-check
/tmp/mnemosyne-lock-check/bin/pip install --require-hashes -r requirements.txt
/tmp/mnemosyne-lock-check/bin/python -m pytest tests -q
```

Review package/version changes in the generated diff; do not hand-edit package records or hashes.

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

This is an early scaffold. Do **not** expose port `8765` to the public internet. The current API has no authentication, defaults to `127.0.0.1`, and permits browser CORS only from the local dashboard origins. Treat it as local-only until the Security Guardian layer, auth, and audit controls are implemented.

## Design priorities

1. **Local-first continuity** — memory should survive sessions and devices.
2. **Inspectable cognition** — graphs, files, and skills should be visible and editable.
3. **Small shippable layers** — backend first, then dashboard, then ISO polish.
4. **Security before autonomy** — powerful tools need review, audit, and rollback.

## License

MIT. See [LICENSE](LICENSE).
