prompt_id: PROMPT-02
branch: project-gate-prompt-02-behavioral-coverage
handoff_status: updated_after_pr_inspector_yellow_recheck
commits:
  initial_prompt_02_range: 04331a3da62ef6c877a87dfb9e8ef065253b1d6b..c9133136972bbbeaad3abc8430706f5ca22111b9
  inspector_followup_range: a09d27709b6bac74b404f01c4306f0f76269fa46..9c07caa2b9ded5548c915f92c49b8ff0d1849d61
  handoff_consistency_update:
    - self_reference: docs: record final successful prompt 02 follow-up CI in handoff
files_changed:
  - .github/workflows/validate.yml
  - docs/BEHAVIORAL_RULE_COVERAGE.md
  - docs/handoffs/PROMPT-02_HANDOFF.md
  - schemas/behavioral-coverage/behavioral-coverage.v1.schema.json
  - schemas/validator-evidence/validator-evidence.v1.schema.json
  - scripts/validate-behavioral-rule-coverage.py
  - src/ev4_transition/behavioral_coverage/__init__.py
  - src/ev4_transition/behavioral_coverage/validator.py
  - src/ev4_transition/cli.py
  - tests/behavioral_coverage/test_behavioral_coverage_validator.py
  - tests/behavioral_coverage/test_behavioral_semantic_fixtures.py
  - tests/behavioral_coverage/test_coverage_cli.py
  - tests/fixtures/behavioral_coverage/valid/critical_rule_fixture_tested.json
  - tests/fixtures/behavioral_coverage/invalid/critical_rule_prose_only.json
  - tests/fixtures/behavioral_coverage/invalid/critical_rule_schema_backed_without_followup.json
  - tests/fixtures/behavioral_coverage/invalid/downstream_contract_missing_for_claimed_enforcement.json
  - tests/fixtures/result_envelope/valid/accepted_with_all_required_evidence_shape.json
  - tests/fixtures/result_envelope/valid/synthetic_fixture_labeled.json
  - tests/fixtures/result_envelope/valid/output_write_success.json
  - tests/fixtures/result_envelope/invalid/accepted_missing_validator_evidence.json
  - tests/fixtures/result_envelope/invalid/accepted_with_failed_validator_evidence.json
  - tests/fixtures/result_envelope/invalid/accepted_with_unknown_validator_evidence.json
  - tests/fixtures/result_envelope/invalid/accepted_with_malformed_validator_evidence.json
  - tests/fixtures/result_envelope/invalid/accepted_with_unpinned_validator_evidence.json
  - tests/fixtures/result_envelope/invalid/accepted_with_validator_hash_mismatch.json
  - tests/fixtures/result_envelope/invalid/accepted_with_validator_stage_mismatch.json
  - tests/fixtures/result_envelope/invalid/synthetic_only_marked_as_real_evidence.json
  - tests/fixtures/result_envelope/invalid/output_write_failed_but_success.json
  - tests/fixtures/stage_bundle/valid/project_gate_owned_schema_only.json
  - tests/fixtures/stage_bundle/invalid/copied_specialist_schema_claimed_as_project_gate_owned.json
  - tests/fixtures/stage_bundle/invalid/project_gate_schema_prefix_collision_specialist_copy.json
tests_run:
  - local isolated generated-tree check before original PR: PYTHONPATH=src python scripts/validate-behavioral-rule-coverage.py docs/BEHAVIORAL_RULE_COVERAGE.md -> exit 0
  - local isolated generated-tree check before original PR: PYTHONPATH=src python -m ev4_transition.cli coverage validate docs/BEHAVIORAL_RULE_COVERAGE.md -> exit 0
  - local isolated generated-tree check before original PR: PYTHONPATH=src pytest -q tests/behavioral_coverage -> 17 passed
  - GitHub Actions run 28718131721 on head c9133136972bbbeaad3abc8430706f5ca22111b9: success, but PR Inspector found uncovered negative paths
  - PR Inspector v1.4.0 break attempts reproduced PRF-001 through PRF-004 against head c9133136972bbbeaad3abc8430706f5ca22111b9
  - GitHub Actions run 28718851101 on reviewed head 9c07caa2b9ded5548c915f92c49b8ff0d1849d61: success
  - PR Inspector v1.4.0 recheck on head 9c07caa2b9ded5548c915f92c49b8ff0d1849d61: YELLOW_CHANGES_OR_VERIFICATION_REQUIRED due only to stale handoff CI wording
tests_passed:
  - Original isolated generated-tree behavioral coverage script check
  - Original isolated generated-tree behavioral coverage CLI check
  - Original isolated generated-tree behavioral coverage pytest suite: 17 passed
  - GitHub Actions run 28718131721 on old head c9133136972bbbeaad3abc8430706f5ca22111b9
  - GitHub Actions run 28718851101 on reviewed head 9c07caa2b9ded5548c915f92c49b8ff0d1849d61
tests_failed:
  - PRF-001 on old head c9133136972bbbeaad3abc8430706f5ca22111b9: fake ci_enforced evidence references were accepted
  - PRF-002 on old head c9133136972bbbeaad3abc8430706f5ca22111b9: failed validator evidence was accepted
  - PRF-003 on old head c9133136972bbbeaad3abc8430706f5ca22111b9: schema ownership prefix collision was accepted
  - PRF-004 on old head c9133136972bbbeaad3abc8430706f5ca22111b9: unreadable/invalid schema path could bypass structured CLI exit behavior
tests_not_run:
  - local full repository python -m pip install -e '.[dev]'
  - local full repository pytest after Inspector fixes
  - local full repository ev4-transition coverage validate docs/BEHAVIORAL_RULE_COVERAGE.md after Inspector fixes
  - local npm run status
  - local npm run validate
ci_evidence:
  old_head:
    head_sha: c9133136972bbbeaad3abc8430706f5ca22111b9
    run_id: 28718131721
    workflow: Skeleton Health
    conclusion: success
    note: Inspector found uncovered negative paths, so this CI success did not close PRF-001 through PRF-004.
  reviewed_followup_head:
    head_sha: 9c07caa2b9ded5548c915f92c49b8ff0d1849d61
    merge_sha: 06f363c6b7caa2f8e3ba143c2b6dc379df9f9bb9
    run_id: 28718851101
    workflow: Skeleton Health
    conclusion: success
    successful_jobs:
      - skeleton
      - python-core
    successful_key_steps:
      - Run Project Gate Python tests
      - Behavioral coverage validator
      - Behavioral fixture validation
      - Verify no specialist canonical schema files exist
      - Official Architect validator fixture suite
      - Official CE validator fixture suite
      - Generated Architect-to-CE transition smoke and CE binding
  note: This handoff records concrete CI evidence for the reviewed follow-up head. For any later commit, GitHub PR checks remain the source of truth; do not infer future CI status from this static file.
coverage_rules_advanced:
  - PG-BRC-001: resolves repository-relative carriers, validators, fixtures, and CI step references and emits deterministic evidence_records.
  - PG-EVIDENCE-001: accepted result requires validator-evidence.v1 records with status=passed, pinning, stage match, hash match, and result digest.
  - PG-SYNTH-001: synthetic_only_marked_as_real_evidence fixture isolates synthetic guard with otherwise complete validator evidence.
  - PG-SCHEMA-001: Project Gate-owned schema check moved from prefix matching to exact schema registry; prefix collision fixture added.
  - PG-OUTPUT-001: output write failure with success status remains fixture-tested with complete validator evidence shape.
  - PG-BOUNDARY-001: schema ownership anti-drift covers explicit copied schema and prefix-collision cases.
  - PG-DOWNSTREAM-001: false downstream_contract_enforced claim prevention remains fixture-tested; downstream_contract_enforced is still not claimed.
coverage_rules_still_gap:
  - PG-ADAPTER-001: runner/official adapter boundary enforcement is deferred to PROMPT-03.
  - PG-DOWNSTREAM-001: real downstream contract and rejection evidence for CE-to-Builder/Builder-to-Responsive remain insufficient_evidence.
  - PG-PROGRESS-001: handoff/report no-false-progress linter not implemented.
  - PG-OUTPUT-001: full Persian RTL/LTR UX report fixtures deferred to PROMPT-06.
  - PG-STATUS-001: legacy valid compatibility still exists in current A2C/stage-bundle paths.
new_diagnostics:
  - PG_BRC_CARRIER_REFERENCE_INVALID
  - PG_BRC_VALIDATOR_REFERENCE_INVALID
  - PG_BRC_VALIDATOR_SYMBOL_NOT_FOUND
  - PG_BRC_FIXTURE_REFERENCE_INVALID
  - PG_BRC_FIXTURE_NOT_BOUND_TO_VALIDATOR
  - PG_BRC_CI_STEP_REFERENCE_INVALID
  - PG_BRC_CI_JOB_REFERENCE_INVALID
  - PG_BRC_DOWNSTREAM_CONTRACT_REFERENCE_INVALID
  - PG_BRC_DOWNSTREAM_REJECTION_FIXTURE_REFERENCE_INVALID
  - PG_EVIDENCE_VALIDATOR_EVIDENCE_MALFORMED
  - PG_EVIDENCE_VALIDATOR_STATUS_NOT_PASSED
  - PG_EVIDENCE_VALIDATOR_UNPINNED
  - PG_EVIDENCE_VALIDATOR_STAGE_MISMATCH
  - PG_EVIDENCE_VALIDATOR_SCOPE_MISMATCH
  - PG_EVIDENCE_VALIDATOR_HASH_MISMATCH
  - PG_EVIDENCE_VALIDATOR_RESULT_DIGEST_INVALID
  - PG_SCHEMA_REGISTRY_PATH_MISSING
new_or_changed_cli:
  - ev4-transition coverage inspect
  - ev4-transition coverage validate
  - ev4-transition coverage validate returns exit 2 for unreadable or invalid schema paths via CoverageSourceError.
  - coverage reports include deterministic evidence_records for resolved carriers, validators, fixtures, and CI steps.
new_or_changed_ci:
  - .github/workflows/validate.yml schema allowlist includes schemas/behavioral-coverage/behavioral-coverage.v1.schema.json.
  - .github/workflows/validate.yml schema allowlist includes schemas/validator-evidence/validator-evidence.v1.schema.json.
  - .github/workflows/validate.yml runs python scripts/validate-behavioral-rule-coverage.py docs/BEHAVIORAL_RULE_COVERAGE.md.
  - .github/workflows/validate.yml runs ev4-transition coverage validate docs/BEHAVIORAL_RULE_COVERAGE.md.
  - .github/workflows/validate.yml runs pytest tests/behavioral_coverage.
important_design_decisions:
  - Behavioral coverage validation is separate from normal transition validation in Phase 1 and does not block ordinary user transition validation unless explicitly run.
  - Evidence reference resolution is repository-relative and rejects external, absolute, missing, and traversal-like references.
  - Validator references use file or file::symbol form; unresolved module strings are rejected.
  - Workflow step evidence is resolved from the actual YAML step name.
  - Fixture-to-validator binding is deterministic by validator family and fixture directory.
  - Exact Project Gate schema registry replaced prefix matching for Project Gate-owned schema claims.
  - validator-evidence.v1 is Project Gate-owned evidence metadata; it is not a copied specialist schema.
  - PG-DOWNSTREAM-001 is not marked downstream_contract_enforced; it is fixture_tested only for false downstream enforcement claim prevention.
  - No CE constructability logic, Builder runtime logic, Responsive repair logic, or new transition orchestration was added.
web_sources_used: []
next_allowed_prompt: PROMPT-03 after current PR head CI is green and owner accepts/merges PR #18
blocking_issues: []
remaining_insufficient_evidence:
  - PR Inspector final green recheck after this handoff consistency update
  - real CE-to-Builder downstream rejection evidence
  - real Builder-to-Responsive downstream rejection evidence
  - official Builder adapter execution evidence
  - official Responsive validation evidence
  - final evidence gate policy, fixtures, and CI evidence
merge_note:
  - This handoff no longer claims that GitHub Actions run 28718851101 is pending.
  - Do not merge on this file alone; merge readiness still requires current PR checks and owner confirmation.
