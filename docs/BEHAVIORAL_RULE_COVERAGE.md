# Behavioral Rule Coverage

Status: `PROMPT-05` extends the conservative Project Gate ledger without replacing the established CE→Builder, runner, adapter, or downstream rules.

This ledger intentionally separates implementation and CI evidence from behavioral coverage status. Builder→Responsive and Final Evidence Gate checks now have exact-head CI wiring, immutable lock reproduction, and official Responsive validator execution, but they remain `validator_backed` until dedicated behavioral fixtures are bound to their declared validators. No rule is promoted merely because a workflow is green.

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
  "generated_by": "PROMPT-05 conservative additive ledger",
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
      "next_enforcement_step": "Add dedicated C2B behavioral fixtures bound to the lock verifier before promotion.",
      "notes": "C2B lock verification has CI evidence, but the behavioral status remains below ci_enforced."
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
      "next_enforcement_step": "Add dedicated C2B behavioral fixtures bound to the smoke validator before promotion.",
      "notes": "The C2B smoke uses an owner fixture; it is integration evidence, not real handoff evidence."
    },
    {
      "rule_id": "PG-VALIDATOR-001",
      "rule": "Official validators must execute only through Project Gate runner infrastructure and fail closed when missing, timed out, unparseable, or failed.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/responsive_tools.py", "src/ev4_transition/runners/subprocess_runner.py", "src/ev4_transition/runners/failure_mapping.py"],
      "validators": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/responsive_tools.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/prompt-05.yml / Run pinned official Responsive validators"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Missing or failed validator execution must never be treated as acceptance.",
      "next_enforcement_step": "Add dedicated runner behavioral fixtures for Responsive validator failure modes before promotion.",
      "notes": "Owner validator execution is wired in CI but remains distinct from real responsive evidence."
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
      "notes": "Builder adapter path has CI evidence, but fixture-bound behavioral promotion remains pending."
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
      "next_enforcement_step": "Do not mark downstream_contract_enforced until owner rejection fixtures are pinned and proven.",
      "notes": "Prompt-05 proves orchestration and owner-validator integration, not downstream contract enforcement."
    },
    {
      "rule_id": "PG-B2R-001",
      "rule": "Builder→Responsive dependency locks must be reproduced from exact pinned Builder and Responsive owner file bytes.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["contracts/locks/builder-to-responsive-transition.v1.lock.json", "src/ev4_transition/transitions/builder_to_responsive.py", "scripts/compute-builder-to-responsive-lock.py"],
      "validators": ["src/ev4_transition/transitions/builder_to_responsive.py", "scripts/compute-builder-to-responsive-lock.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/prompt-05.yml / Recompute and compare immutable locks"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Mutable refs or stale hashes can authorize the wrong owner boundary.",
      "next_enforcement_step": "Add dedicated lock-behavior fixtures bound to the B2R verifier before promotion.",
      "notes": "The committed B2R lock is computed from immutable owner commits; this is not real handoff evidence."
    },
    {
      "rule_id": "PG-B2R-002",
      "rule": "Builder→Responsive intake must use the Responsive-owned schema and official boundary validator through runner infrastructure.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/runners/responsive_tools.py"],
      "validators": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/runners/responsive_tools.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests", ".github/workflows/prompt-05.yml / Run pinned official Responsive validators"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Project Gate must not invent Responsive intake meaning or bypass the owner validator.",
      "next_enforcement_step": "Bind dedicated B2R behavioral fixtures to the transition validator before promotion.",
      "notes": "Accepted intake remains input eligibility only and is not Responsive correctness."
    },
    {
      "rule_id": "PG-FINAL-001",
      "rule": "Final Evidence Gate must verify an immutable prior lock chain and the official Responsive output validator before acceptance.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["contracts/locks/final-gate.v1.lock.json", "src/ev4_transition/transitions/final_gate.py", "scripts/compute-final-gate-lock.py", "src/ev4_transition/runners/responsive_tools.py"],
      "validators": ["src/ev4_transition/transitions/final_gate.py", "scripts/compute-final-gate-lock.py", "src/ev4_transition/runners/responsive_tools.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/prompt-05.yml / Recompute and compare immutable locks", ".github/workflows/prompt-05.yml / Run pinned official Responsive validators"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "An incomplete prior chain or bypassed owner validator can create false final acceptance.",
      "next_enforcement_step": "Add dedicated final-gate behavioral fixtures and real non-synthetic Responsive evidence before promotion.",
      "notes": "Final Gate orchestration is implemented; production, release, accessibility, export, and frontend correctness remain unclaimed."
    },
    {
      "rule_id": "PG-EVIDENCE-001",
      "rule": "Synthetic fixtures, raw screenshots, and CI success must not be treated as real frontend or production evidence.",
      "risk": "Critical",
      "status": "validator_backed",
      "target_status": "validator_backed",
      "carriers": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py", "docs/STATUS_DECISION_MATRIX.md"],
      "validators": ["src/ev4_transition/transitions/builder_to_responsive.py", "src/ev4_transition/transitions/final_gate.py"],
      "valid_fixtures": [],
      "invalid_fixtures": [],
      "ci_steps": [".github/workflows/validate.yml / Prompt-05 transition tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Synthetic or CI-only evidence can create unsupported correctness and readiness claims.",
      "next_enforcement_step": "Bind dedicated evidence-classification fixtures before promotion and retain insufficient_evidence for missing real evidence.",
      "notes": "No real non-synthetic Builder→Responsive or final evidence is claimed."
    }
  ]
}
```

## PROMPT-05 notes

- Existing C2B, runner, adapter, and downstream rules remain present and unchanged in authority.
- B2R and Final Gate rules remain `validator_backed`; exact-head CI does not automatically promote behavioral status.
- `PG-DOWNSTREAM-001` remains below `downstream_contract_enforced`.
- Synthetic fixtures, screenshots, and CI success are not real EV4 handoff or frontend correctness evidence.
