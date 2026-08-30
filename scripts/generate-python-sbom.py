#!/usr/bin/env python3
"""Generate a deterministic CycloneDX inventory for the active Python environment."""

from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path
import re
from urllib.parse import quote


def canonical_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def installed_components() -> list[dict[str, str]]:
    by_name: dict[str, dict[str, str]] = {}
    for distribution in metadata.distributions():
        try:
            raw_name = distribution.metadata["Name"]
        except KeyError:
            continue
        if not raw_name:
            continue
        name = canonical_name(raw_name)
        version = distribution.version
        purl = f"pkg:pypi/{quote(name, safe='-')}@{quote(version, safe='.-+')}"
        by_name[name] = {
            "type": "library",
            "bom-ref": purl,
            "name": name,
            "version": version,
            "purl": purl,
        }
    return sorted(by_name.values(), key=lambda component: component["name"].casefold())


def build_document() -> dict[str, object]:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "mnemosyne-os-python-environment",
                "version": "0.1.0-dev",
            }
        },
        "components": installed_components(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(build_document(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
