# Project Gate Evidence Truth Spine

## Scope

This document defines the lean runtime authority path for consequential Project Gate transitions.

```text
Referenced or Embedded Artifact
→ Safe Resolution
→ Exact Byte Read
→ SHA-256 Verification
→ Schema Validation
→ Claim / Subject / Viewport Binding
→ Positive-Proof Policy
→ Runtime-derived Classification
→ Transition Authorization
→ Single Publication Gate
```

The implementation remains local to Project Gate. It does not create a second transition engine, an authorization service, a generalized evidence graph, or a cryptographic attestation system.

## Evidence policy registry

Operational evidence uses a small explicit registry keyed by evidence type.

| Evidence type | Required positive proof |
|---|---|
| Architect, Builder, Responsive, and Kernel-owned artifacts | Accepted official owner validator |
| Viewport runtime artifacts | Valid `ev4_runtime_evidence_receipt_v1` receipt |

An unavailable, skipped, unknown, or non-accepted owner validator never authorizes operational evidence. Artifact existence, a matching digest, schema shape, or absence of suspicious words is not positive proof.

Keyword and fixture-marker scanning remains a rejection signal only. It may classify evidence as `synthetic`; it can never create `real_verified`.

## Canonical classification

Caller-authored fields such as `synthetic`, `real_evidence`, `evidence_status`, `verification_status`, and `classification` are retained only as metadata. They are not authorization inputs.

```text
real_verified =
    source_resolved
    and hash_verified
    and schema_valid
    and claim_binding_valid
    and subject_binding_valid
    and positive_proof_verified
    and not synthetic_conflict
```

Classifications:

- `real_verified`: every required predicate above is true.
- `synthetic`: an authoritative artifact or receipt contains a derived synthetic conflict.
- `insufficient_evidence`: positive proof, bytes, digest, schema, or binding evidence is missing or not accepted.

A renamed fixture with valid JSON and a valid hash remains `insufficient_evidence` unless its evidence-type policy is positively satisfied.

## Runtime evidence receipt

Viewport evidence has no owner validator, so it requires a lightweight local receipt stored beside the artifact by default:

```text
<artifact_ref>.receipt.json
```

Receipt schema:

```yaml
schema: ev4_runtime_evidence_receipt_v1
evidence_type: viewport_artifact
viewport: desktop
run_id: RUN-...
subject_ref: ...
artifact_ref: ...
artifact_sha256: ...
producer_commit: ...
capture_status: completed
validation_status: accepted
```

The receipt authorizes only when:

- the receipt exists and is valid JSON;
- its artifact hash equals the exact resolved artifact bytes;
- `subject_ref`, `viewport`, and `artifact_ref` match;
- its `run_id` matches the runtime artifact;
- `producer_commit` matches the pinned producer context;
- capture and validation statuses are accepted.

No signatures, keys, external attestation, or network service are involved.

## Publication authority

Operational publication uses one predicate:

```text
publication_allowed =
    transition_authorized
    and handoff_allowed
    and evidence_ready
    and validation_passed
```

The predicate is evaluated before path resolution, staging, downstream JSON creation, receipt generation, or publication.

When false, the operation returns diagnostics only:

```yaml
handoff_allowed: false
publication_allowed: false
downstream_artifact:
  status: not_published
receipt:
  status: not_generated
```

No downstream handoff file or publication receipt may be created.

## Boundary behavior

### Architect → CE / Producer integration

- Official Architect and CE validators remain authoritative.
- `handoff.allowed=false` stops before all publication work.
- Synthetic or insufficient evidence cannot publish.
- Consequential final-artifact hashes continue to be recomputed from canonical embedded objects or exact referenced bytes.

### CE → Builder

The existing C2B publication behavior remains unchanged. Its pre-publication early return stays authoritative.

### Builder → Responsive

Source-bound Builder artifacts require accepted pinned owner validators. Viewport artifacts require valid runtime receipts. Session, package, action-set, claim, subject, and viewport bindings remain fail-closed.

### Final Gate

Responsive output requires its accepted official owner validator. Desktop, tablet, and mobile artifacts require valid runtime receipts. Raw Kernel intake remains mandatory and internally executed. Supplied projections remain non-authoritative and drift-checked.

## Capability truth

This repair does not assert a real non-synthetic ecosystem handoff. Capability status remains `insufficient_evidence` until an actual source-bound operator run produces accepted owner validations and valid runtime receipts.
