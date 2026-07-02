from __future__ import annotations

import hashlib
from importlib import metadata
from pathlib import Path
from typing import Any

from .canonical_json import canonical_bytes, canonical_hash


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_canonical_json(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def package_version() -> str:
    try:
        return metadata.version("ev4-project-gate")
    except metadata.PackageNotFoundError:
        return "0.1.0-local"


def transition_provenance(source: dict[str, Any], transition: dict[str, Any], output: dict[str, Any], timestamp: str | None = None) -> dict[str, Any]:
    data = {
        "source_stage": source["stage"],
        "target_stage": transition["target_stage"],
        "transition_id": transition["transition_id"],
        "transition_version": transition["version"],
        "source_hash": canonical_hash(source),
        "output_hash": canonical_hash(output),
        "tool": "ev4-project-gate",
        "tool_version": package_version(),
    }
    if timestamp:
        data["timestamp"] = timestamp
    if source.get("provenance"):
        data["source_provenance"] = source["provenance"]
    return data
