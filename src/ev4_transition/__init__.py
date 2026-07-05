"""EV4 Project Gate deterministic core.

The package implements Stage Evidence Bundle validation, Architect-to-CE
orchestration, and the CE-to-Builder orchestration baseline. CE-to-Builder
is not exposed as a general public CLI transition, and real non-synthetic
handoff evidence remains insufficient.
"""

from .canonical_json import CANONICAL_JSON_VERSION, canonical_bytes, canonical_dumps, canonical_sha256
from .bundle_validator import BundleValidator

__all__ = [
    "BundleValidator",
    "CANONICAL_JSON_VERSION",
    "canonical_bytes",
    "canonical_dumps",
    "canonical_sha256",
]
