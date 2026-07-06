"""EV4 Project Gate deterministic core.

The package implements Stage Evidence Bundle validation, Architect-to-CE
orchestration, and guarded fail-closed CLI entries for the CE-to-Builder, Builder-to-Responsive,
and Final Evidence Gate orchestration baselines. Real non-synthetic handoff
evidence remains insufficient.
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
