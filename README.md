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

What is still future work:

- Full custom ISO build/test cycle
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
├── docs/index.html                 # GitHub Pages site
├── mnemosyne/
│   ├── core/memory.py              # Local memory store + graph builder
│   ├── services/api_server.py      # FastAPI server
│   ├── skills/store.py             # Starter skill store
│   └── tugboat/router.py           # Declarative routing stub
├── scripts/
│   ├── install-local.sh            # Local dev installer
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
- `GET /skills`
- `POST /skills`
- `POST /tugboat/route`

## Custom Ubuntu / Cubic path

The practical path toward a true Mnemosyne OS ISO is Ubuntu + Cubic first, not a from-scratch distro.

Inside a Cubic chroot, after copying this repo to `/opt/mnemosyne-os`, run:

```bash
cd /opt/mnemosyne-os
sudo ./scripts/build-mnemosyne-os.sh
```

That script:

- creates a non-root `mnemosyne` service user
- installs Python dependencies in `/opt/mnemosyne-os/.venv`
- seeds starter memory/skills into `/var/lib/mnemosyne`
- installs a systemd service on port `8765`
- installs `/usr/local/bin/mnemosyne`
- adds a desktop launcher for the dashboard

## Security note

This is an early scaffold. Do **not** expose port `8765` to the public internet. The current API has no authentication. Treat it as local-only until the Security Guardian layer, auth, and audit controls are implemented.

## Design priorities

1. **Local-first continuity** — memory should survive sessions and devices.
2. **Inspectable cognition** — graphs, files, and skills should be visible and editable.
3. **Small shippable layers** — backend first, then dashboard, then ISO polish.
4. **Security before autonomy** — powerful tools need review, audit, and rollback.

## License

MIT. See [LICENSE](LICENSE).
