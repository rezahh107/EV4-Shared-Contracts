# AGENTS.md

## Repository Purpose

`EV4-Shared-Contracts` is a non-authoritative cross-repository compatibility gate for:

```text
rezahh107/EV4-Architect-Repo
rezahh107/EV4-Constructability-Engineer-Repo
rezahh107/EV4-Builder-Assistant-Repo
rezahh107/EV4-Responsive-Architect
```

The four repositories remain authoritative for their own schemas, validators, adapters, fixtures, and runtime behavior.

```yaml
current_mode: role_transition_complete_python_not_started
canonical_schema_owner: false
runtime_dependency: false
repair_authority: false
```

## Read First

1. `AGENTS.md`
2. `README.md`
3. relevant compatibility manifests and rules, when present
4. exact producer and consumer contracts in the owning repositories
5. generated reports, when present

Documents about canonical promotion or the previous skeleton role are historical context when they conflict with `README.md` or this file.

## Operating Scope

This repository may host:

- deterministic Python compatibility verification;
- versioned compatibility manifests and rules;
- Producer → Adapter → Consumer execution tests;
- field-preservation and semantic-invariant checks;
- controlled synthetic fixtures identified as synthetic;
- canonical JSON reports with pinned repository refs and SHA-256 evidence;
- CI for cross-repository compatibility verification.

This repository does not own canonical EV4 schemas, replace repo-local validators, act as a runtime dependency, repair the four repositories automatically, or choose architectural authority.

## Verification Model

```text
Producer schema and validator
            ↓
      validated fixture
            ↓
 documented adapter/normalizer
            ↓
Consumer schema and validator
            ↓
preservation and semantic rules
            ↓
deterministic compatibility report
```

A schema diff is an observation, not complete compatibility proof.

## Evidence Policy

Findings should retain repository refs, file paths, fixture identity and digest, executed commands, exit codes, rule IDs and versions, and source/target paths when applicable.

Evidence states:

```text
observed
validated
resolved
derived
proposed
unverified
insufficient_evidence
```

A shape check is not full Producer validation. Synthetic fixtures are not real Elementor or EV4 exports.

Keep these findings distinct:

```text
structural_difference
intentional_compatible_transformation
confirmed_contract_incompatibility
repair_owner_unresolved
```

## Initial Python Phase

```text
CE valid fixture
→ CE schema and validator
→ Builder adapter
→ Builder schema and validator
→ preservation checks
→ semantic checks
→ canonical JSON report
```

Initial diagnostic targets:

```text
producer_variant_not_supported_by_adapter
required_field_lost
```

Later phases may add generated boundary cases, property-based tests, mutation testing, and issue fingerprinting.

## Determinism

Machine-readable outputs use stable ordering, versioned canonical JSON, SHA-256 over canonical content, explicit UTF-8 and timezone handling, deterministic diagnostics, pinned repository refs, and retained subprocess results.

## Reporting

User-facing reports are written in Persian. Repository names, refs, paths, schema IDs, rule IDs, commands, workflow names, and diagnostic codes remain in English.

## Guardrail

This repository verifies compatibility evidence. It is not a fifth architectural authority and does not convert undocumented assumptions into executable truth.
