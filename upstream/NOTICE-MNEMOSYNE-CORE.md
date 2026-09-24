# Mnemosyne authoritative core notice

Mnemosyne OS consumes the public Mnemosyne core from
[atxgreene/Mnemosyne](https://github.com/atxgreene/Mnemosyne).
It is the sole authoritative L0–L5 implementation. Phase 1 packages that
upstream release; it does not create another cognitive implementation.

No Mnemosyne core source is copied into this repository. The Arch recipe builds
the upstream source archive at exact commit
`bbaffde0b8cd8fca2ff08a3cec08d2e763c76982`, verified by SHA-256 as recorded in
[`mnemosyne-core.lock.json`](mnemosyne-core.lock.json). The existing local
`mnemosyne/` tree is a separate historical compatibility fixture pending later
migration; it is not part of the installed authoritative distribution.

- Canonical repository: https://github.com/atxgreene/Mnemosyne
- Version/tag metadata: `0.9.8` / `v0.9.8`
- Pinned license: https://raw.githubusercontent.com/atxgreene/Mnemosyne/bbaffde0b8cd8fca2ff08a3cec08d2e763c76982/LICENSE
- Pinned license SHA-256: `3f4582bcef89d07c0504ed023dad80cdb526bf529bd4e8fb04a87e19332ab3b7`

## Pinned MIT license text

```text
MIT License

Copyright (c) 2026 atxgreene

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
