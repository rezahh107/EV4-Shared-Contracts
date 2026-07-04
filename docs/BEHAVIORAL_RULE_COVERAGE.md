# Behavioral Rule Coverage

Status: `PROMPT-00` audit/freeze baseline. This file records current behavioral enforcement status honestly. It does not claim enforcement without a carrier, validator, fixture, CI step, or downstream contract.

Allowed statuses:

```text
prose_only
schema_backed
validator_backed
fixture_tested
ci_enforced
downstream_contract_enforced
```

## Coverage table

| Rule ID | Rule | Current carrier | Validator | Fixture/test | CI | Downstream evidence | Current status | Next enforcement step |
|---|---|---|---|---|---|---|---|---|
| `PG-BOUNDARY-001` | Project Gate must remain an orchestrator/checkpoint, not a specialist engine. | `README.md`, `AGENTS.md`, `docs/ROLE_BOUNDARY_MAP.md` | Partial: schema allowlist in CI prevents unexpected copied schema files. | No dedicated boundary scanner. | Partial via `.github/workflows/validate.yml` schema allowlist. | Specialist repo boundary docs. | `ci_enforced` for schema-copy subset; broader rule remains partial. | Add static boundary scanner for forbidden specialist logic/imports/prose claims. |
| `PG-SCHEMA-001` | Project Gate must not copy specialist schemas as competing canonical contracts. | `AGENTS.md`, `docs/VALIDATION_STRATEGY.md`, workflow schema allowlist. | Workflow `find schemas` allowlist. | CI checks only current `schemas/` files. | `.github/workflows/validate.yml` skeleton job. | Specialist schemas remain in owner repos. | `ci_enforced` | Extend scanner to future contract folders and lock manifests. |
| `PG-EVIDENCE-001` | No accepted/final result without explicit evidence. | Stage Bundle schema; validators; docs. | `BundleValidator`; Architect→CE result schema. | Valid/invalid/insufficient-evidence fixtures; A2C tests. | Python CI smoke tests. | Limited to Stage Bundle and A2C synthetic fixtures. | `fixture_tested` | Align transition statuses with `accepted/repair_needed/insufficient_evidence/invalid` and add negative accepted-without-evidence fixtures. |
| `PG-SYNTH-001` | Synthetic fixtures must not be treated as real EV4 evidence. | README, AGENTS, Stage Bundle `synthetic`, docs. | Stage Bundle schema requires `synthetic`. | Synthetic fixtures exist. | CLI smoke and pytest run in CI. | No real downstream evidence. | `fixture_tested` | Add report-level guard that blocks real-readiness wording when `synthetic=true` or verification is `synthetic_fixture_only`. |
| `PG-ADAPTER-001` | Project Gate may call official adapters but must not implement specialist adapter logic. | A2C mapping exists; Builder adapter documented in Builder repo. | Current Project Gate does not yet call Builder adapter. | None for CE→Builder in Project Gate. | None in Project Gate. | Builder adapter contract and registry exist downstream. | `prose_only` for future adapters; A2C has implemented deterministic projection only because CE-owned mapping is pinned. | In `PROMPT-03/04`, isolate adapter execution behind runner and prove no internal Builder adapter implementation. |
| `PG-VALIDATOR-001` | Project Gate must call official specialist validators where transition claims depend on them. | `validator_runner.py`; A2C transition. | Architect and CE validators called by subprocess when local checkouts supplied. | A2C transition tests and CI smoke. | Python CI runs official Architect and CE validator fixture suites. | Architect/CE official validators exist. | `ci_enforced` for A2C only. | Generalize runner boundary for future validator execution. |
| `PG-HASH-001` | Canonical JSON/file-byte hashes must be deterministic. | `canonical_json.py`; `external_lock.py`; schemas. | Canonical hash functions and lock verifier. | `tests/test_canonical_json.py`, lock/transition tests. | Python CI runs pytest and lock verification. | External contract locks use file bytes. | `ci_enforced` for current core/A2C. | Add Unicode no-normalization regression fixture and future transition hash tests. |
| `PG-LOCK-001` | External locks must verify pinned repo/ref/path/hash/identity and not trust themselves. | `external_lock.py`; `contracts/locks/architect-to-ce-transition.v1.lock.json`. | `verify_external_contract_lock`. | A2C tests and `scripts/verify-architect-to-ce-lock.py`. | Python CI runs lock verification. | Architect/CE pinned files. | `ci_enforced` for A2C. | Add lock schema/validator for future CE→Builder and Builder→Responsive locks. |
| `PG-STATUS-001` | Status decisions must be evidence-driven and fail closed. | Current schemas and CLI exit codes. | `status_from_diagnostics`; schema validation. | CLI and validator tests. | CLI smoke tests. | Partial; current schemas use `valid`, not target `accepted`. | `fixture_tested` | Create Project Gate transition decision model with `accepted/repair_needed/insufficient_evidence/invalid`. |
| `PG-OUTPUT-001` | Machine-readable JSON and Persian summaries must be truthful. | CLI `_emit`; `persian_summary`. | Result schemas validate JSON; Persian is minimal. | CLI tests include Persian insufficient evidence. | Python CI grep checks Persian insufficient-evidence phrase. | No full UX contract enforcement. | `fixture_tested` | Add Persian RTL/LTR report fixtures and status icon + text + tone checks in `PROMPT-06`. |
| `PG-UNICODE-001` | Project Gate must not silently normalize Unicode for canonical hashing. | `canonical_json.py` currently preserves strings through `json.dumps`. | No explicit Unicode normalization scanner/test observed. | No dedicated regression fixture observed. | Not separately enforced. | None. | `prose_only` / implicit implementation behavior only. | Add explicit normalization-difference hash regression tests. |
| `PG-PROGRESS-001` | Project Gate reports must not claim unexecuted progress. | README/AGENTS no-false-execution policy; handoff requirement. | No validator for progress claims. | No fixture. | No CI. | None. | `prose_only` | Add handoff/report schema or linter for executed/not-run/test fields. |
| `PG-BRC-001` | Behavioral coverage must be tracked honestly. | This file. | None yet. | None yet. | None yet. | None. | `prose_only` | Add behavioral coverage schema/validator/fixtures/CI in `PROMPT-02`. |
| `PG-DOWNSTREAM-001` | Downstream rejection evidence is required before claiming downstream compatibility. | Validation strategy docs; downstream validators in specialist repos. | A2C has Architect/CE validators; future transitions not wired. | Synthetic A2C fixtures only. | A2C official validator CI only. | CE/Builder/Responsive rejection evidence exists in owner repos but not orchestrated by Project Gate for future transitions. | `ci_enforced` for A2C only; `prose_only` for CE→Builder and Builder→Responsive. | In `PROMPT-04/05`, run official downstream gates/adapters and capture rejection fixtures. |

## Critical / High gaps

```yaml
critical:
  - PG-ADAPTER-001 for CE-to-Builder and Builder-to-Responsive is prose_only in Project Gate.
  - PG-DOWNSTREAM-001 is not enforced for CE-to-Builder or Builder-to-Responsive.
  - PG-EVIDENCE-001 does not yet cover target accepted/repair_needed transition semantics.
  - PG-STATUS-001 has naming/model drift between current validation schemas and target transition decision model.
high:
  - PG-BRC-001 has no schema/validator/fixture/CI yet.
  - PG-UNICODE-001 lacks explicit no-normalization regression tests.
  - PG-PROGRESS-001 lacks automated no-false-progress/handoff validation.
  - PG-OUTPUT-001 Persian UX is minimal and not yet full RTL/LTR/report-contract enforced.
```

## Rules advanced by PROMPT-00

```yaml
advanced:
  - PG-BRC-001: carrier created as docs/BEHAVIORAL_RULE_COVERAGE.md
  - PG-BOUNDARY-001: role boundary carrier refreshed
  - PG-DOWNSTREAM-001: live downstream boundary gaps recorded
not_advanced_to_enforcement:
  - no validator added
  - no fixture added
  - no CI step added
  - no transition implementation added
```

## Enforcement honesty note

No Critical/High future-transition rule should be described as fully enforced until the required carrier, official validator/adapter execution, fixture, CI step, and downstream rejection evidence exist.