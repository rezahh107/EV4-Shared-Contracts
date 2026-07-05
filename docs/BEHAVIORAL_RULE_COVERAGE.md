# Behavioral Rule Coverage

Status: `PROMPT-05` extends the conservative ledger for Builder→Responsive and Final Gate. No rule is promoted to `ci_enforced` or `downstream_contract_enforced` unless a concrete carrier, validator/fixture, and CI/downstream proof exists.

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
  "generated_by": "PROMPT-05 Builder→Responsive and Final Evidence Gate baseline",
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
      "notes": "This rule is fixture-tested by existing behavioral coverage validator fixtures."
    },
    {
      "rule_id": "PG-DOWNSTREAM-001",
      "rule": "Downstream rejection evidence is required before claiming downstream compatibility.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["docs/BEHAVIORAL_RULE_COVERAGE.md", "src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py"],
      "validators": ["tests/transitions/test_builder_to_responsive.py", "tests/transitions/test_final_gate.py"],
      "valid_fixtures": ["tests/fixtures/behavioral_coverage/valid/critical_rule_fixture_tested.json"],
      "invalid_fixtures": ["tests/fixtures/behavioral_coverage/invalid/downstream_contract_missing_for_claimed_enforcement.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral coverage validator", ".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Project Gate must not claim downstream_contract_enforced without owner rejection evidence.",
      "next_enforcement_step": "Add Responsive-owned rejection fixtures before any downstream_contract_enforced promotion.",
      "notes": "PROMPT-05 keeps downstream enforcement explicitly unclaimed."
    },
    {
      "rule_id": "PG-EVIDENCE-001",
      "rule": "Accepted transition/final status requires explicit evidence refs and must fail closed when evidence is absent.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py", "docs/STATUS_DECISION_MATRIX.md"],
      "validators": ["tests/transitions/test_builder_to_responsive.py", "tests/transitions/test_final_gate.py"],
      "valid_fixtures": ["tests/fixture_matrix/builder_to_responsive/valid/builder_responsive_input.valid.json"],
      "invalid_fixtures": ["tests/fixture_matrix/builder_to_responsive/invalid/missing_mobile_evidence.invalid.json"],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Missing evidence can otherwise be silently upgraded to acceptance.",
      "next_enforcement_step": "Bind real owner evidence bundles once available.",
      "notes": "Fixture tests cover missing Builder evidence, missing viewport evidence, and missing final real evidence."
    },
    {
      "rule_id": "PG-SYNTH-001",
      "rule": "Synthetic fixtures and raw screenshots must not be treated as real EV4 evidence.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py"],
      "validators": ["tests/transitions/test_builder_to_responsive.py::test_builder_to_responsive_raw_screenshot_does_not_prove_correctness", "tests/transitions/test_final_gate.py::test_final_gate_does_not_count_synthetic_as_real_evidence"],
      "valid_fixtures": [],
      "invalid_fixtures": ["tests/fixture_matrix/builder_to_responsive/invalid/missing_mobile_evidence.invalid.json"],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Synthetic evidence or screenshots can create false frontend confidence.",
      "next_enforcement_step": "Add owner-supplied real evidence fixtures.",
      "notes": "Raw screenshot and synthetic-only branches emit insufficient_evidence."
    },
    {
      "rule_id": "PG-HASH-001",
      "rule": "Pinned lock manifests must verify repository, commit, path, identity marker, and SHA-256 file bytes.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["contracts/locks/builder-to-responsive-transition.v1.lock.json", "contracts/locks/final-gate.v1.lock.json", "src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py"],
      "validators": ["verify_builder_to_responsive_lock", "verify_final_gate_lock"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Wrong pins or stale owner files can authorize the wrong boundary.",
      "next_enforcement_step": "Refresh placeholder lock hashes from live owner checkouts before promoting.",
      "notes": "Prompt-05 lock files intentionally contain placeholders and therefore remain fail-closed."
    },
    {
      "rule_id": "PG-VALIDATOR-001",
      "rule": "Official validators must fail closed when missing, unavailable, failed, or unverifiable.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "validators": ["tests/transitions/test_builder_to_responsive.py", "tests/transitions/test_final_gate.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Absent Responsive validator execution must not unlock accepted.",
      "next_enforcement_step": "Run live owner validator smoke in CI with owner checkouts.",
      "notes": "Prompt-05 adds tests for missing Responsive schema/validator."
    },
    {
      "rule_id": "PG-OUTPUT-001",
      "rule": "Project Gate-owned output/result envelopes must validate against Project Gate-owned result schemas.",
      "risk": "High",
      "status": "fixture_tested",
      "target_status": "fixture_tested",
      "carriers": ["schemas/builder-to-responsive-transition-result/builder-to-responsive-transition-result.v1.schema.json", "schemas/final-gate-result/final-gate-result.v1.schema.json"],
      "validators": ["tests/transitions/test_builder_to_responsive.py::test_builder_to_responsive_result_schema_validated", "tests/transitions/test_final_gate.py::test_final_gate_result_schema_validated"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Invalid result envelopes can hide fail-closed diagnostics.",
      "next_enforcement_step": "Add broader result fixture matrix if output writing expands.",
      "notes": "Prompt-05 validates B2R and Final Gate result envelopes."
    }
  ]
}
```

## PROMPT-05 notes

- `PG-DOWNSTREAM-001` remains below `downstream_contract_enforced`.
- `PG-HASH-001` remains `validator_backed` because Prompt-05 lock files intentionally use honest placeholders until exact owner hashes are refreshed.
- CI success and raw screenshots are not frontend correctness evidence.
- Synthetic fixtures are not real EV4 handoff evidence.
