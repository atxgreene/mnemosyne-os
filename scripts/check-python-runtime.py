#!/usr/bin/env python3
"""Fail fast when Mnemosyne OS is run with an unsupported Python."""

import sys
from typing import Optional, Sequence


MINIMUM_VERSION = (3, 11)


def runtime_error(version_info: Sequence[int], executable: str) -> Optional[str]:
    """Return an actionable error for unsupported runtimes, otherwise ``None``."""
    observed = ".".join(str(part) for part in version_info[:3])
    if tuple(version_info[:2]) >= MINIMUM_VERSION:
        return None
    return (
        "Mnemosyne OS requires Python >=3.11; "
        f"observed Python {observed} at {executable}"
    )


def main() -> int:
    current_version = (
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro,
    )
    error = runtime_error(current_version, sys.executable)
    if error is not None:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
