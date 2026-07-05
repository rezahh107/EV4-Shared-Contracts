# Behavioral Rule Coverage

Status: `PROMPT-04` CE→Builder baseline has passing GitHub Actions evidence on PR `#20` head `87a4a84640c999cee049a0d40865c25efabeafb0` / run `28741498875`.

This ledger is intentionally conservative. CE→Builder lock/tool orchestration passed CI, but the behavioral coverage validator requires fixture bindings before a rule is marked `ci_enforced`. Therefore the C2B rules remain `validator_backed` here until dedicated C2B behavioral fixtures are bound to the declared validators.

Allowed statuses:

```text
prose_only
schema_backed
validator_backed
fixture_tested
ci_enforced
downstream_contract_enforced
```

## Machine-readable coverage ledger

```json behavioral-coverage.v1
{
  "schema_version": "behavioral-coverage.v1",
  "generated_by": "PROMPT-04 CE-to-Builder conservative ledger refresh for PR #20",
  "rules": [
    {
      "rule_id": "PG-BRC-001",
      "rule": "Behavioral coverage must be tracked honestly.",
      "risk": "High",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["docs/BEHAVIORAL_RULE_COVERAGE.md", "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_coverage_document", "scripts/validate-behavioral-rule-coverage.py"],
      "valid_fixtures": ["tests/fixtures/behavioral_coverage/valid/critical_rule_fixture_tested.json"],
      "invalid_fixtures": ["tests/fixtures/behavioral_coverage/invalid/critical_rule_prose_only.json", "tests/fixtures/behavioral_coverage/invalid/critical_rule_schema_backed_without_followup.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral coverage validator"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "False behavioral coverage can make weak rules look enforced.",
      "next_enforcement_step": "Keep future status promotions evidence-backed and fixture-bound.",
      "notes": "This rule is fixture-tested by the behavioral coverage validator fixtures."
    },
    {
      "rule_id": "PG-C2B-001",
      "rule": "CE→Builder lock pins must match exact owner repository, commit, path, identity marker, and SHA-256 file bytes.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["contracts/locks/ce-to-builder-transition.v1.lock.json", "src/ev4_transition/transitions/ce_to_builder.py", "scripts/verify-ce-to-builder-lock.py"],
      "validators": ["scripts/verify-ce-to-builder-lock.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / CE-to-Builder lock verification", ".github/workflows/validate.yml / Compute CE-to-Builder lock hashes"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Wrong pins or hashes allow stale or unintended owner contracts to govern Builder handoff.",
      "next_enforcement_step": "Add dedicated C2B behavioral fixtures bound to the lock verifier before promoting this ledger entry to ci_enforced.",
      "notes": "The CI step passed on run 28741498875, but this ledger keeps the behavioral status below ci_enforced until fixture binding is added."
    },
    {
      "rule_id": "PG-C2B-002",
      "rule": "CE→Builder transition must call official CE validator, official Builder gate, official Builder adapter, and official Builder output validator in order.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/transitions/ce_to_builder.py", "src/ev4_transition/runners/official_tools.py", "scripts/ce-to-builder-smoke.py"],
      "validators": ["scripts/ce-to-builder-smoke.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / CE-to-Builder transition pytest", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Bypassing the Builder gate lets invalid CE output reach Builder normalization.",
      "next_enforcement_step": "Add dedicated C2B behavioral fixtures bound to the smoke validator before promoting this ledger entry to ci_enforced.",
      "notes": "The CI smoke passed on run 28741498875 using an owner fixture; it is integration evidence, not real handoff evidence."
    },
    {
      "rule_id": "PG-VALIDATOR-001",
      "rule": "Official validators must execute only through Project Gate runner infrastructure and fail closed when missing, timed out, unparseable, or failed.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py", "src/ev4_transition/runners/failure_mapping.py"],
      "validators": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Missing or failed validator execution must never be treated as acceptance.",
      "next_enforcement_step": "Add runner behavioral fixtures for official validator failure modes before promotion.",
      "notes": "C2B owner validator path passed in CI, but fixture-bound behavioral promotion remains pending."
    },
    {
      "rule_id": "PG-ADAPTER-001",
      "rule": "Official adapters must execute only through runner infrastructure; fallback adapters are forbidden and missing/timeouts fail closed.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py", "src/ev4_transition/runners/failure_mapping.py"],
      "validators": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Fallback or missing adapter behavior can invent a next-stage package without owner evidence.",
      "next_enforcement_step": "Add runner behavioral fixtures for adapter failure modes before promotion.",
      "notes": "Builder adapter path passed in CI, but fixture-bound behavioral promotion remains pending."
    },
    {
      "rule_id": "PG-DOWNSTREAM-001",
      "rule": "Downstream rejection evidence is required before claiming downstream compatibility.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["docs/BEHAVIORAL_RULE_COVERAGE.md", "src/ev4_transition/behavioral_coverage/validator.py"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_coverage_document"],
      "valid_fixtures": ["tests/fixtures/behavioral_coverage/valid/critical_rule_fixture_tested.json"],
      "invalid_fixtures": ["tests/fixtures/behavioral_coverage/invalid/downstream_contract_missing_for_claimed_enforcement.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral coverage validator"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Future transitions must not claim downstream_contract_enforced without owner rejection evidence.",
      "next_enforcement_step": "Do not mark CE-to-Builder downstream_contract_enforced until Builder-owned rejection fixtures are pinned and proven.",
      "notes": "PROMPT-04 proves orchestration, not downstream_contract_enforced status."
    }
  ]
}
```

## PROMPT-04 notes

- `PG-C2B-001` and `PG-C2B-002` have passing CI evidence on run `28741498875`, but the behavioral ledger keeps them at `validator_backed` until dedicated fixture bindings are added.
- `PG-DOWNSTREAM-001` remains below `downstream_contract_enforced`.
- Synthetic/owner-fixture smoke is integration evidence, not real EV4 handoff evidence.
