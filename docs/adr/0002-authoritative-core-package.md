# ADR 0002: Package the authoritative Mnemosyne core

- **Status:** Accepted
- **Date:** 2026-09-24
- **Scope:** Phase 1 authoritative-core packaging

## Context

Phase 0 established a distro-independent package boundary. The upstream
[`atxgreene/Mnemosyne`](https://github.com/atxgreene/Mnemosyne) project now has
a verified public `v0.9.8` release with SQLite/FTS persistence, canonical
commands, and the complete six-tier memory model.

This repository also contains an older `mnemosyne/` FastAPI/JSONL
implementation and a Debian live ISO around it. Leaving their relationship
implicit would make package ownership and migration status ambiguous.

## Decision

`atxgreene/Mnemosyne` is the sole authoritative L0–L5 implementation. Mnemosyne
OS consumes it immutably from an exact commit and verified SHA-256, as recorded
in [`upstream/mnemosyne-core.lock.json`](../../upstream/mnemosyne-core.lock.json).
The release tag and version are descriptive metadata; mutable references are
never execution authority.

The Arch package builds the upstream wheel from that commit-pinned source
archive. This repository does not fork or copy cognition. It owns only the
downstream provenance, package recipe, service policy, smoke tests, and future
integration layers. Full pinned MIT attribution is preserved in
[`upstream/NOTICE-MNEMOSYNE-CORE.md`](../../upstream/NOTICE-MNEMOSYNE-CORE.md).

The package installs a hardened systemd user service. It binds
`mnemosyne-serve` to loopback, writes under the user's state directory, names
an explicit projects directory, and keeps automatic proposal application off.
Installation does not enable or start the unit automatically.

## Compatibility boundary

The repository's existing `mnemosyne/` FastAPI/JSONL implementation and Debian
live ISO remain runnable as a historical compatibility fixture pending later migration.
This legacy path remains runnable throughout Phase 1. It supports current regression and developer-preview workflows, but it is not a second
authoritative core and must not gain competing L0–L5 cognition semantics.

Phase 1 does not migrate the legacy CLI, API, JSONL data, Debian image, or ISO
smoke path onto the new package. It also does not deliver the thin adapter or
owned image. Those remain later, separately tested migration layers.

## Consequences

- Arch/Omarchy users can build a package from an immutable public source input.
- Package smoke tests exercise the installed upstream distribution rather than
  importing the repository's legacy modules.
- Core upgrades require deliberate commit, archive hash, wheel metadata,
  license, contract, and smoke-test review.
- The future thin adapter and future owned image must consume this package;
  neither may embed another cognitive implementation.
