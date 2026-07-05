# Behavioral Rule Coverage

Status: `PROMPT-04` CE→Builder baseline has passing GitHub Actions evidence on PR `#20` head `87a4a84640c999cee049a0d40865c25efabeafb0` / run `28741498875`.

This ledger stays conservative: CE→Builder lock/tool orchestration can be marked `ci_enforced`; real non-synthetic CE→Builder handoff evidence and downstream Builder→Responsive compatibility are still not proven.

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
  "generated_by": "PROMPT-04 CE-to-Builder green CI refresh for PR #20",
  "rules": [
    {
      "rule_id": "PG-BRC-001",
      "rule": "Behavioral coverage must be tracked honestly.",
      "risk": "High",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["docs/BEHAVIORAL_RULE_COVERAGE.md", "schemas/behavioral-coverage/behavioral-coverage.v1.schema.json"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_coverage_document", "scripts/validate-behavioral-rule-coverage.py"],
      "valid_fixtures": ["tests/fixtures/behavioral_coverage/valid/critical_rule_fixture_tested.json"],
      "invalid_fixtures": ["tests/fixtures/behavioral_coverage/invalid/critical_rule_prose_only.json", "tests/fixtures/behavioral_coverage/invalid/critical_rule_schema_backed_without_followup.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral coverage validator"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "False behavioral coverage can make weak rules look enforced.",
      "next_enforcement_step": "Keep future promotions evidence-backed.",
      "notes": "Latest checked PR head passed the behavioral coverage validator."
    },
    {
      "rule_id": "PG-EVIDENCE-001",
      "rule": "No accepted result without explicit evidence.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["schemas/transition-result/transition-result.v1.schema.json", "schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json", "schemas/validator-evidence/validator-evidence.v1.schema.json", "src/ev4_transition/runners/records.py"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_transition_result_semantics"],
      "valid_fixtures": ["tests/fixtures/result_envelope/valid/accepted_with_all_required_evidence_shape.json"],
      "invalid_fixtures": ["tests/fixtures/result_envelope/invalid/accepted_missing_validator_evidence.json", "tests/fixtures/result_envelope/invalid/accepted_with_failed_validator_evidence.json", "tests/fixtures/result_envelope/invalid/accepted_with_unknown_validator_evidence.json", "tests/fixtures/result_envelope/invalid/accepted_with_malformed_validator_evidence.json", "tests/fixtures/result_envelope/invalid/accepted_with_unpinned_validator_evidence.json", "tests/fixtures/result_envelope/invalid/accepted_with_validator_hash_mismatch.json", "tests/fixtures/result_envelope/invalid/accepted_with_validator_stage_mismatch.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral fixture validation", ".github/workflows/validate.yml / CE-to-Builder transition pytest", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Accepted without explicit validator/gate/adapter/output evidence is a false execution claim.",
      "next_enforcement_step": "Require real handoff evidence before claiming production transition evidence.",
      "notes": "CI smoke proves orchestration against pinned owner tools using an owner fixture; it is not real non-synthetic handoff evidence."
    },
    {
      "rule_id": "PG-SYNTH-001",
      "rule": "Synthetic fixtures must not be treated as real EV4 evidence.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["schemas/stage-bundle/stage-bundle.v1.schema.json", "src/ev4_transition/behavioral_coverage/validator.py", "tests/fixture_matrix/ce_to_builder/insufficient-evidence/synthetic-only-not-real-evidence.json"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_transition_result_semantics"],
      "valid_fixtures": ["tests/fixtures/result_envelope/valid/synthetic_fixture_labeled.json"],
      "invalid_fixtures": ["tests/fixtures/result_envelope/invalid/synthetic_only_marked_as_real_evidence.json"],
      "ci_steps": [".github/workflows/validate.yml / Behavioral fixture validation", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Synthetic owner-fixture smoke can prove wiring only; it is not real transition evidence.",
      "next_enforcement_step": "Keep real-evidence requirement fail-closed for production handoffs.",
      "notes": "PROMPT-04 smoke labels owner fixture evidence as integration evidence only."
    },
    {
      "rule_id": "PG-SCHEMA-001",
      "rule": "Project Gate must not copy specialist schemas as competing canonical contracts.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["schemas/README.md", ".github/workflows/validate.yml", "src/ev4_transition/behavioral_coverage/validator.py"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_stage_bundle_semantics"],
      "valid_fixtures": ["tests/fixtures/stage_bundle/valid/project_gate_owned_schema_only.json"],
      "invalid_fixtures": ["tests/fixtures/stage_bundle/invalid/copied_specialist_schema_claimed_as_project_gate_owned.json", "tests/fixtures/stage_bundle/invalid/project_gate_schema_prefix_collision_specialist_copy.json"],
      "ci_steps": [".github/workflows/validate.yml / Verify no specialist canonical schema files exist", ".github/workflows/validate.yml / Behavioral fixture validation"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Copied schemas produce contract drift and false canonical ownership.",
      "next_enforcement_step": "Keep CE and Builder payload schemas pinned and external.",
      "notes": "CE→Builder result schema is Project Gate-owned result envelope, not a copied specialist schema."
    },
    {
      "rule_id": "PG-BOUNDARY-001",
      "rule": "Project Gate must remain an orchestrator/checkpoint, not a specialist engine.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["README.md", "AGENTS.md", "docs/ROLE_BOUNDARY_MAP.md", "src/ev4_transition/behavioral_coverage/validator.py", "scripts/check-runner-boundary.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "validators": ["src/ev4_transition/behavioral_coverage/validator.py::validate_stage_bundle_semantics", "scripts/check-runner-boundary.py"],
      "valid_fixtures": ["tests/fixtures/stage_bundle/valid/project_gate_owned_schema_only.json"],
      "invalid_fixtures": ["tests/fixtures/stage_bundle/invalid/copied_specialist_schema_claimed_as_project_gate_owned.json", "tests/fixtures/stage_bundle/invalid/project_gate_schema_prefix_collision_specialist_copy.json"],
      "ci_steps": [".github/workflows/validate.yml / Verify no specialist canonical schema files exist", ".github/workflows/validate.yml / Static runner-boundary scanner", ".github/workflows/validate.yml / Runner boundary tests"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Boundary drift turns Project Gate into a fifth specialist engine or hides unsafe execution.",
      "next_enforcement_step": "Continue keeping specialist logic in owner repositories.",
      "notes": "PROMPT-04 keeps official CE/Builder tool execution inside runner infrastructure."
    },
    {
      "rule_id": "PG-VALIDATOR-001",
      "rule": "Official validators must execute only through Project Gate runner infrastructure and fail closed when missing, timed out, unparseable, or failed.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py", "src/ev4_transition/runners/failure_mapping.py"],
      "validators": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "valid_fixtures": [],
      "invalid_fixtures": ["tests/fixture_matrix/ce_to_builder/invalid/synthetic-fallback-adapter-forbidden.json"],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/validate.yml / CE-to-Builder transition pytest", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Missing or failed validator execution must never be treated as acceptance.",
      "next_enforcement_step": "Keep validator failure mapping covered as owner tools evolve.",
      "notes": "Latest CI passed CE validator, Builder gate, and Builder output validator paths."
    },
    {
      "rule_id": "PG-ADAPTER-001",
      "rule": "Official adapters must execute only through runner infrastructure; fallback adapters are forbidden and missing/timeouts fail closed.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py", "src/ev4_transition/runners/failure_mapping.py"],
      "validators": ["src/ev4_transition/runners/official_tools.py", "src/ev4_transition/runners/subprocess_runner.py"],
      "valid_fixtures": [],
      "invalid_fixtures": ["tests/fixture_matrix/ce_to_builder/invalid/synthetic-fallback-adapter-forbidden.json"],
      "ci_steps": [".github/workflows/validate.yml / Runner tests", ".github/workflows/validate.yml / CE-to-Builder transition pytest", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Fallback or missing adapter behavior can invent a next-stage package without owner evidence.",
      "next_enforcement_step": "Keep Builder adapter smoke pinned to owner artifact revisions.",
      "notes": "Builder adapter is called only after Builder gate passes."
    },
    {
      "rule_id": "PG-C2B-001",
      "rule": "CE→Builder lock pins must match exact owner repository, commit, path, identity marker, and SHA-256 file bytes.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["contracts/locks/ce-to-builder-transition.v1.lock.json", "src/ev4_transition/transitions/ce_to_builder.py", "scripts/verify-ce-to-builder-lock.py"],
      "validators": ["src/ev4_transition/transitions/ce_to_builder.py::verify_ce_to_builder_lock", "scripts/verify-ce-to-builder-lock.py"],
      "valid_fixtures": [],
      "invalid_fixtures": ["tests/fixture_matrix/ce_to_builder/invalid/synthetic-fallback-adapter-forbidden.json"],
      "ci_steps": [".github/workflows/validate.yml / Compute CE-to-Builder lock hashes", ".github/workflows/validate.yml / CE-to-Builder lock verification"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Wrong pins or hashes allow stale or unintended owner contracts to govern Builder handoff.",
      "next_enforcement_step": "Recompute and verify hashes whenever pinned owner artifacts change.",
      "notes": "Exact file-byte SHA-256 values are committed and lock verification passed in run 28741498875."
    },
    {
      "rule_id": "PG-C2B-002",
      "rule": "CE→Builder transition must call official CE validator, official Builder gate, official Builder adapter, and official Builder output validator in order.",
      "risk": "Critical",
      "status": "ci_enforced",
      "target_status": "ci_enforced",
      "carriers": ["src/ev4_transition/transitions/ce_to_builder.py", "src/ev4_transition/runners/official_tools.py", "scripts/ce-to-builder-smoke.py"],
      "validators": ["src/ev4_transition/transitions/ce_to_builder.py", "scripts/ce-to-builder-smoke.py"],
      "valid_fixtures": [],
      "invalid_fixtures": ["tests/fixture_matrix/ce_to_builder/invalid/synthetic-fallback-adapter-forbidden.json"],
      "ci_steps": [".github/workflows/validate.yml / CE-to-Builder transition pytest", ".github/workflows/validate.yml / CE-to-Builder live owner tool smoke"],
      "downstream_contracts": [],
      "downstream_rejection_fixtures": [],
      "documented_risk": "Bypassing the Builder gate lets invalid CE output reach Builder normalization.",
      "next_enforcement_step": "Replace integration fixture evidence with real non-synthetic handoff evidence when available.",
      "notes": "Smoke uses a Builder-owned fixture and is integration evidence only, not real handoff evidence."
    },
    {
      "rule_id": "PG-DOWNSTREAM-001",
      "rule": "Downstream rejection evidence is required before claiming downstream compatibility.",
      "risk": "Critical",
      "status": "fixture_tested",
      "target_status": "downstream_contract_enforced",
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

- `PG-C2B-001` and `PG-C2B-002` are `ci_enforced` for the PROMPT-04 baseline on run `28741498875`.
- `PG-DOWNSTREAM-001` remains below `downstream_contract_enforced`.
- Synthetic/owner-fixture smoke is integration evidence, not real EV4 handoff evidence.
