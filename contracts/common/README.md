# Project Gate common contracts

This directory contains Project Gate-owned cross-repository contracts that complement the canonical single-stage Stage Evidence Bundle.

- `producer-gate-export.v1.schema.json`: run-level Producer export that strictly references Stage Evidence Bundle v1.
- `common-contract-lock.v1.schema.json`: immutable exact-byte vendoring lock.

These contracts do not own Producer-specific payload schemas or stage sequences. Producer adoption remains pending until exact merged bytes are vendored and enforced in Producer CI.
