# ADR 0001: Omarchy-compatible substrate boundary

- **Status:** Accepted
- **Date:** 2026-08-30
- **Scope:** Phase 0.1 substrate contracts

## Context

Mnemosyne needs a distribution path without coupling its cognitive core to one desktop, package repository, image builder, or Linux distribution. The repository already contains a Debian v0.1 developer-preview live-build path. That preview remains useful as a historical fixture and regression surface, but it is not the target architecture.

Omarchy is the first integration target because it offers an opinionated desktop, ISO tooling, and package infrastructure. Those upstreams evolve independently. Mnemosyne therefore needs an explicit ownership boundary, immutable upstream provenance, and safety invariants before any adapter or image work begins.

## Decision

Mnemosyne core is distro-independent. The delivery order is:

1. **Portable service/package first.** After the Phase 0 contracts, the first implementation layer will be a generic Linux/Arch package plus a hardened systemd user service. It can be installed and removed without owning the host distribution. That layer is future implementation work, not something delivered by this Phase 0.1 PR.
2. **Thin, optional adapter second.** Omarchy integration is a thin, optional adapter around the portable package, not a second cognitive implementation.
3. **Owned ISO is last.** Any eventual Mnemosyne-owned thin image is downstream packaging assembled only after the portable package and adapter boundaries are proven.

The existing Debian v0.1 preview is preserved as a historical fixture. Maintaining it does not make Debian the core substrate and does not imply that the future Omarchy adapter or owned image exists today.

Under the target architecture, `atxgreene/Mnemosyne` is the sole authoritative cognitive implementation. Distribution adapters package or configure that core; they do not fork its memory, policy, or cognition semantics.

This repository's currently bundled `mnemosyne/` JSONL v0.1 implementation remains a historical developer-preview compatibility fixture pending migration to the authoritative core. Its current runnable behavior is documented honestly, but it must not accrue competing long-term memory, policy, or cognition semantics.

JSONL is temporary compatibility/import infrastructure in the target architecture. JSONL is a temporary compatibility/import-only surface, not a second cognitive core.

Omarchy inputs are recorded in [`upstream/omarchy.lock.json`](../../upstream/omarchy.lock.json). A 40-hex `commit_sha` is the only execution and pinning authority. A tag or branch is human-readable metadata only. Applicable attribution is preserved in [`upstream/NOTICE-OMARCHY.md`](../../upstream/NOTICE-OMARCHY.md).

## Safety and reversibility invariants

- Integrations ship as reversible packages with explicit install, upgrade, rollback, and removal boundaries.
- No memory, model, shell plugin, or AI agent output may directly authorize privileged commands.
- The service remains loopback-only and same-origin until a separately reviewed authentication and authorization threat model exists.
- Snapshots do not replace ICMS backups. Image or filesystem rollback is operational recovery, not durable cognitive-memory continuity.
- Omarchy agent auto-approval or permission-bypass defaults must not be inherited.
- Upstream code is reviewed at the immutable commit recorded in the lock before it is copied, built, or executed.

## Rejected alternatives

### Source merger

Rejected. Merging Omarchy source into Mnemosyne would blur ownership, make upstream updates difficult to audit, and couple cognitive-core releases to distro internals.

### Full fork

Rejected. A full fork would create an unnecessary downstream distribution maintenance burden and invite divergence from Omarchy security and packaging work. If an owned image is eventually justified, it remains a thin assembly over reviewed immutable inputs rather than a general-purpose Omarchy fork.

### ISO-first delivery

Rejected. Image-first work would hard-code integration choices before portability, rollback, privilege, backup, and package lifecycle contracts are proven.

## Consequences

- Phase 0 can advance through contracts and portable packaging without importing Omarchy source.
- Omarchy updates are deliberate lock changes with license review, not implicit branch movement.
- The current Debian fixture remains testable while no longer defining the future substrate architecture.
- An adapter and an owned image remain future work until each earlier layer has verified install, removal, backup, and privilege behavior.
