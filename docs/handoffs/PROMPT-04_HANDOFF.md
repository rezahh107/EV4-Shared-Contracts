prompt_id: PROMPT-04
branch: project-gate-prompt-04-ce-to-builder
commits:
  - 0af2e48feddff904fef3aaffbd078afbf682d1c9 feat(c2b): add transition package exports
  - 378c55a890e08dac5636fb4a6f556c13340ae5ce feat(c2b): add official CE and Builder runner helpers
  - 89167d2721bbf4f3a11612eec72218acb69270f4 feat(c2b): export official tool runner helpers
  - 067d6194693d5fb74d4527f5af306ad762c96327 feat(c2b): map owner gate and output validator failures
  - 89d6c39a3523f19af72e0c5ef203322eecad30c1 feat(c2b): support text validators and adapter output hashes
  - 99e9017a24e2498338d415f3fc3f66d5eceed019 feat(c2b): implement CE to Builder transition orchestration
  - ddee20754aa87562eb8369a408bdc14a21df4b22 feat(c2b): add CE to Builder transition result schema
  - 24868ab441fae40975ba6cecf16d92b1dd5f5091 chore(c2b): add fail-closed CE to Builder lock baseline
  - 4ef6d9f2141e927ac10cda7e66e30368fafe34a6 test(c2b): add CE to Builder transition fixture matrix tests
  - 70a5a8e2a45988198beb59a3193c6c074c66e9e5 test(c2b): add CE to Builder fixture matrix README
  - 2117c5b1e6f9a4c3a5f1374f53474c7940e44fbc test(c2b): add positive synthetic fixture label
  - 43d72d97cb951c1511bd05922e7f8b0878556502 test(c2b): add fallback adapter negative fixture label
  - 70fbe1bc47f3ec33dc21ea3230a3b6fd4995a6a2 test(c2b): add synthetic evidence insufficient fixture label
files_changed:
  - contracts/locks/ce-to-builder-transition.v1.lock.json
  - schemas/ce-to-builder-transition-result/ce-to-builder-transition-result.v1.schema.json
  - src/ev4_transition/runners/__init__.py
  - src/ev4_transition/runners/failure_mapping.py
  - src/ev4_transition/runners/official_tools.py
  - src/ev4_transition/runners/subprocess_runner.py
  - src/ev4_transition/transitions/__init__.py
  - src/ev4_transition/transitions/ce_to_builder.py
  - tests/fixture_matrix/ce_to_builder/README.md
  - tests/fixture_matrix/ce_to_builder/valid/synthetic-ce-package-label.json
  - tests/fixture_matrix/ce_to_builder/invalid/synthetic-fallback-adapter-forbidden.json
  - tests/fixture_matrix/ce_to_builder/insufficient-evidence/synthetic-only-not-real-evidence.json
  - tests/transitions/test_ce_to_builder.py
tests_run:
  - python -m py_compile /mnt/data/official_tools.py /mnt/data/failure_mapping.py /mnt/data/subprocess_runner.py /mnt/data/ce_to_builder_concise.py /mnt/data/test_ce_to_builder_short.py
tests_passed:
  - local py_compile passed for drafted Python files before GitHub write
tests_failed: []
tests_not_run:
  - pytest tests/transitions/test_ce_to_builder.py
  - pytest tests/runners
  - python scripts/check-runner-boundary.py
  - full GitHub Actions CI
coverage_rules_advanced:
  - PG-ADAPTER-001: runner helpers and tests added, not CI proven
  - PG-VALIDATOR-001: CE validator, Builder gate, and Builder output validator runner paths added, not CI proven
  - PG-EVIDENCE-001: CE→Builder result accepted_requires schema added, not CI proven
  - PG-HASH-001: synthetic lock verification tests added, live hashes unresolved
  - PG-DOWNSTREAM-001: synthetic Builder gate/output rejection tests added, not downstream_contract_enforced
  - PG-SYNTH-001: synthetic-only evidence fixture/test added
coverage_rules_still_gap:
  - live CE/Builder file-byte SHA-256 lock values are placeholders and fail closed
  - docs/BEHAVIORAL_RULE_COVERAGE.md was not updated in this execution slice
  - docs/TRANSITION_BOUNDARY_MAP.md was not updated in this execution slice
  - docs/IMPLEMENTATION_STATUS.yaml was not updated in this execution slice
new_diagnostics:
  - PG.C2B.* diagnostics in src/ev4_transition/transitions/ce_to_builder.py
  - PG.ADAPTER.EXECUTION_FAILED
new_or_changed_cli:
  - none; Python API only in PROMPT-04 slice
new_or_changed_ci:
  - none; CI update remains gap
important_design_decisions:
  - Project Gate calls official CE and Builder tools only through src/ev4_transition/runners/*.
  - Builder gate blocks adapter execution.
  - Builder adapter output is parsed from stdout JSON and its stdout hash is recorded as output_hash.
  - Builder-owned output schema is read from the Builder owner checkout; Project Gate does not copy Builder schema.
  - Lock manifest uses verified owner paths/commits but intentionally placeholder SHA-256 values because exact live file-byte hashes could not be computed in this environment.
web_sources_used: []
next_allowed_prompt: continue_PROMPT-04F_docs_CI_lock_hash_completion_before_PROMPT-05
blocking_issues:
  - Exact live owner file-byte SHA-256 values must be computed from local/CI checkouts and replace all-zero lock placeholders.
  - CI workflow and canonical docs still need updates before DoD is complete.
  - Pytest and GitHub Actions were not run by the assistant.
remaining_insufficient_evidence:
  - exact_file_byte_sha256_values_for_contracts/locks/ce-to-builder-transition.v1.lock.json
  - pytest_result_for_tests/transitions/test_ce_to_builder.py
  - static_runner_boundary_result_after_new_transition_module
  - GitHub_Actions_result_for_project-gate-prompt-04-ce-to-builder
  - live_CE_validator_smoke_result
  - live_Builder_gate_smoke_result
  - live_Builder_adapter_smoke_result
  - docs_BEHAVIORAL_RULE_COVERAGE_update
  - docs_TRANSITION_BOUNDARY_MAP_update
  - docs_IMPLEMENTATION_STATUS_update
