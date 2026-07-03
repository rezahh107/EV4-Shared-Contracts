from __future__ import annotations

import re
from typing import Any

from .canonical_json import CANONICAL_JSON_VERSION, canonical_sha256

RFC3339_UTC_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def hash_record(value: str, scope: str) -> dict[str, str]:
    return {
        "algorithm": "sha256",
        "canonicalization": CANONICAL_JSON_VERSION,
        "scope": scope,
        "value": value,
    }


def source_bundle_hash(bundle: Any) -> dict[str, str]:
    return hash_record(canonical_sha256(bundle), "source_bundle")


def canonical_payload_hash(payload: Any) -> dict[str, str]:
    return hash_record(canonical_sha256(payload), "payload")


def preserve_provenance(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_provenance": bundle.get("provenance"),
        "produced_by": bundle.get("produced_by"),
    }


def validate_rfc3339_utc(value: str) -> bool:
    return bool(RFC3339_UTC_PATTERN.fullmatch(value))
