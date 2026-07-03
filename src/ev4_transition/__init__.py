"""EV4 Project Gate deterministic core.

This package currently implements the Stage Evidence Bundle validation
foundation only. It does not implement real EV4 stage transitions.
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
