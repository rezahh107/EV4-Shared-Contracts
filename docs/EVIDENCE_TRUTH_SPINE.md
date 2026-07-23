# Project Gate Evidence Truth Spine

## Scope

This document describes the lean runtime authority path used by consequential Project Gate transitions.

```text
Referenced or Embedded Artifact
→ Safe Resolver
→ Byte Read
→ SHA-256 Recalculation
→ Owner Validator
→ Runtime-derived Classification
→ Claim and Subject Compatibility
→ Transition Authorization
→ Safe Publication
```

The implementation is intentionally local to Project Gate. It does not create a second transition engine, a second Preflight authority, a cross-repository service, a generalized evidence graph, or a cryptographic attestation system.

## Canonical classification

The caller cannot select the authoritative classification.

- `real_verified`: source bytes were resolved, the declared digest matched the computed digest, the applicable owner validator accepted or no owner validator exists for that narrowly scoped evidence item, claim/subject bindings are valid, and no synthetic marker was derived.
- `synthetic`: any authoritative source contains a synthetic or fixture marker, including nested provenance, producer references, source types, fixture paths, IDs, or explicit synthetic flags.
- `insufficient_evidence`: source bytes are unavailable, a digest cannot be verified, owner validation is unavailable where required, or a consequential claim/subject binding is incomplete.

Compatibility fields such as `synthetic`, `real_evidence`, `evidence_status`, and `verification_status` may remain visible as input metadata. They never independently authorize a transition.

## Execution contexts

### Fixture validation

Fixture contract tests may validate shape and diagnostic behavior with `operational=False` where explicitly supported. A synthetic fixture may demonstrate `would_transition`, but it cannot authorize an operational handoff or publication.

### Operational transition

Operational authority requires:

```yaml
preflight_status: ready
classification: real_verified
required_claims_verified: true
```

## Boundary behavior

### Architect → CE / Producer integration

- Synthetic Producer Gate Exports with `handoff.allowed=true` are rejected.
- The consequential final artifact hash is recomputed from the embedded canonical object or referenced file bytes.
- Referenced final artifacts are safe-resolved and compared with the embedded `final_stage_bundle`.

### Builder → Responsive

Reference strings alone are insufficient. Project Gate requires source-bound records under `evidence_bindings`, resolves each file, recomputes its hash, runs the applicable pinned Builder validator, and binds evidence to the Builder Session, source package, Action set, claim class, subject, and viewport.

### Final Gate

Final Gate derives `real_evidence_present` from verified Responsive output and viewport evidence. The raw Kernel intake remains mandatory and is executed internally. A supplied Kernel result remains non-authoritative and is rejected when it drifts from the recomputed result.

Decision-lineage projections remain informational unless a future owner contract explicitly supplies source-bound decision-card authority. The raw Kernel execution is the primary authority.

## Capability truth

This repair does not assert a real non-synthetic ecosystem handoff. Capability status remains `insufficient_evidence` until a source-bound operator artifact is executed successfully against the pinned owner validators.
