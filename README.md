# Mnemosyne OS

**A local-first OS integration project that packages the authoritative Mnemosyne cognitive core while retaining an explicitly separate historical developer-preview fixture.**

> Stellas Hereditabimus — we will inherit the stars.

## Current maturity (September 2026)

Phase 1 is real package work: `mnemosyne-core` builds the authoritative L0–L5 core from the immutable public Mnemosyne v0.9.8 source archive and installs its canonical CLI and loopback service. It is not yet an adapter or a new image.

| Track | Maturity | Scope |
| --- | --- | --- |
| Authoritative core package | Phase 1 — implemented | Arch package and hardened systemd user unit for verified upstream v0.9.8. |
| Debian developer-preview fixture | Maintained historical v0.1 fixture | Existing live-build/QEMU regression path; not the future substrate architecture. |
| Portable service/package | Current — Phase 1 | Distro-independent packaging for the single Mnemosyne cognitive core; Arch is the first recipe. |
| Optional Omarchy adapter | Future — after portable packaging | Thin, removable integration; not an Omarchy source merger or fork. |
| Thin owned image | Eventual — last | Downstream image assembly only after package and adapter contracts are proven. |

Phase 0.1 records the substrate decision in [`docs/adr/0001-omarchy-compatible-substrate.md`](docs/adr/0001-omarchy-compatible-substrate.md), immutable Omarchy provenance in [`upstream/omarchy.lock.json`](upstream/omarchy.lock.json), and applicable MIT notices in [`upstream/NOTICE-OMARCHY.md`](upstream/NOTICE-OMARCHY.md).

Phase 1 records the authoritative-core decision in [`docs/adr/0002-authoritative-core-package.md`](docs/adr/0002-authoritative-core-package.md), exact source/release/license pins in [`upstream/mnemosyne-core.lock.json`](upstream/mnemosyne-core.lock.json), and full attribution in [`upstream/NOTICE-MNEMOSYNE-CORE.md`](upstream/NOTICE-MNEMOSYNE-CORE.md). The package is built by [`packaging/arch/PKGBUILD`](packaging/arch/PKGBUILD), verified by an installed-runtime smoke test, and served with [`packaging/systemd/user/mnemosyne.service`](packaging/systemd/user/mnemosyne.service).

Under the target architecture, `atxgreene/Mnemosyne` is the sole authoritative cognitive implementation. The bundled `mnemosyne/` JSONL v0.1 implementation remains runnable today as a historical developer-preview compatibility fixture pending migration to that authoritative core. It is not the target authoritative core or a second long-term cognitive implementation, and it must not accrue competing long-term memory, policy, or cognition semantics. In Phase 1 it is retained only as a historical compatibility fixture.

The package does not install or replace the legacy fixture. The two paths remain deliberately separate in Phase 1:

- **Authoritative package: usable for Arch package evaluation.** It provides upstream SQLite/FTS persistence, six-tier stats, `mnemosyne-memory`, `mnemosyne-serve`, and the upstream UI on loopback.
- **Bundled v0.1 fixture: usable for local/development workflows today.** It provides a FastAPI server, JSONL memory, search, stats, graph data, Tugboat routing stub, skills store, CLI, and local dashboard.
- **ISO Distribution: experimental developer preview.** `main` builds the legacy Debian Bookworm hybrid ISO and verifies its existing service/API path in QEMU.
- **Not production-ready yet.** There is no completed data migration, packaged thin adapter, owned Arch image, durable ISO persistence story, or hardware USB boot certification.

What you can actually use today:

- Build/install the v0.9.8 authoritative package on Arch and start its user service manually.
- Install and run the bundled v0.1 developer-preview fixture with `scripts/install-local.sh` and `scripts/run-dev.sh`.
- Store/search fixture memories with `python bin/mnemosyne` or use the packaged core's `mnemosyne-memory` command.
- Inspect short-lived package and legacy ISO artifacts from their separate GitHub Actions workflows.

What is still future work:

- Data migration from the historical JSONL fixture into the authoritative SQLite core
- Future thin Omarchy adapter
- Future owned image
- Hardware USB boot testing beyond QEMU
- Persistent writable memory volume in the legacy live ISO
- Profile isolation and reviewed authentication/authorization controls
- Offline local model bundle

## Repository structure

```text
mnemosyne-os/
├── bin/mnemosyne                   # Historical fixture CLI helper
├── dashboard/mnemosyne-panels.html # Historical fixture dashboard
├── docs/
│   ├── adr/                        # Substrate and authoritative-core decisions
│   ├── index.html                  # GitHub Pages site
│   └── plans/                      # Implementation roadmaps
├── iso/                            # Legacy live-build scaffold + ISO test docs
├── kernel/                         # custom-kernel track docs/placeholders
├── mnemosyne/                      # Historical FastAPI/JSONL compatibility fixture
│   ├── core/memory.py
│   ├── services/api_server.py
│   ├── skills/store.py
│   └── tugboat/router.py
├── packaging/
│   ├── arch/                       # Authoritative-core PKGBUILD + installed smoke
│   ├── systemd/user/               # Authoritative-core user service
│   └── install-mnemosyne-os.sh     # Legacy Debian/ISO fixture installer
├── scripts/                        # Legacy fixture and ISO helpers
├── seed/                           # Legacy fixture starter memories and skills
├── tests/                          # Legacy + package/supply-chain contracts
├── upstream/                       # Immutable provenance and attribution
├── LICENSE
└── PHILOSOPHY.md
```

## Authoritative core package (Arch/Omarchy)

On an Arch host, build and install the immutable v0.9.8 package:

```bash
cd packaging/arch
makepkg --syncdeps --install
bash smoke-test.sh
```

The package installs the upstream commands and a user unit, but does not enable
or start it. Start it explicitly when wanted:

```bash
systemctl --user start mnemosyne.service
mnemosyne-memory stats
xdg-open http://127.0.0.1:8484/ui
```

Persistent package state lives under `%S/mnemosyne` (normally
`~/.local/state/mnemosyne`). Automatic proposal application is disabled. The
current package is the portable core layer; the future thin Omarchy adapter
and future owned image are not delivered in Phase 1.

## Quick start (historical fixture)

The instructions below run the separate bundled FastAPI/JSONL compatibility
fixture. They do not install the authoritative package.

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
