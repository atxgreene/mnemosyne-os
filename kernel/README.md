# Mnemosyne OS Kernel Track

The kernel track is intentionally separate from the first flashable ISO milestone.

## Current stance

Mnemosyne OS v0.2 should prove the userspace experience first:

- bootable Linux ISO
- source code on disk at `/opt/mnemosyne-os/source`
- local API service
- CLI
- dashboard
- starter memory/skills
- VM smoke test

Only after that baseline works should this directory grow into kernel config fragments or patches.

## First custom kernel milestone

1. Record the base distro and kernel version used by the verified ISO.
2. Add a config fragment under `kernel/config-fragments/`.
3. Build a distro-native kernel package, not an ad-hoc copied `vmlinuz`.
4. Boot the package in QEMU.
5. Document rollback to the stock kernel.

## Non-goals for now

- No from-scratch kernel patches before the ISO boots.
- No security-sensitive kernel hardening claims without exact config and verification.
- No custom kernel requirement for the first flashable developer preview.
