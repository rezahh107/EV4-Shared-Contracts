# EV4 Project Gate Result Model

Status: `PROMPT-01` Project Gate-owned contract foundation.

## Scope

This document describes Project Gate-owned result envelopes. It does not define any Architect, CE, Builder, or Responsive specialist payload semantics.

## Result schemas

```text
schemas/transition-result/transition-result.v1.schema.json
schemas/architect-to-ce-transition-result/architect-to-ce-transition-result.v1.schema.json
schemas/diagnostic/diagnostic.v1.schema.json
```

`transition-result.v1` is the common Stage Evidence Bundle validation result. It is intentionally narrow:

```yaml
schema_version: transition-result.v1
result_type: stage_bundle_validation
status: accepted | valid | repair_needed | insufficient_evidence | invalid
source_stage: architect | ce | builder | responsive | null
diagnostics: ordered diagnostic list
hashes: source bundle and payload canonical hashes when computable
provenance: preserved input provenance and producer identity
output: null
```

`valid` remains a legacy validation alias for the current Stage Bundle and Architect→CE implementation. The target Project Gate transition vocabulary is:

```text
accepted
repair_needed
insufficient_evidence
invalid
```

`presentation/status_mapping.py` normalizes `valid` to `accepted` for exit-code and Persian presentation purposes.

## Diagnostic ordering

Diagnostics must be deterministic. Current ordering is:

```text
path → severity rank → code → message
```

Severity rank is:

```text
error
insufficient_evidence
warning
info
```

## Hash behavior

Project Gate result hashes use:

```yaml
algorithm: sha256
canonicalization: ev4-canonical-json.v1
encoding: utf8
object_keys: lexicographic
arrays: order_preserved
nan_infinity: rejected
unicode_normalization: not_applied
```

Progress/runtime state must not be appended after final result schema validation and must not be included in canonical result hashes.

## Evidence rule

No result may be presented as `accepted` unless the required evidence for that result scope is explicit. Missing or unresolved evidence must remain `insufficient_evidence`.
