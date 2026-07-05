prompt_id: PROMPT-05
branch: project-gate-prompt-05-builder-responsive-final-gate
commits:
  - b7fd4be62e467b3c08cfc486087bc9b062a348d4
  - ff6f5ee05c3f4a22d62792c6287c8e2ebf06a0ac
  - ef219013de4ad31d1058790b488ac0d5329a4ca7
  - a74f8d093c9590270c4d8f2acdb09c5f6abcaad0
  - 245d0bd0d2cbed53a3ebd249ef410e42124b9ce5
  - 2b5f4437f2f4357353b5092607d5d2d86904f384
  - 04645b79b37dc4b0816213582c8a5e81d3352b57
  - 4098dfc02c3870f9486bd638bca3de60bfb3c5f2
  - d2ac7ebe0d8b2b6a75a2468479c64ff1cc57f594
  - 8d02c1c05eb82c9623833871beaefaeba8a2a858
  - 93b4114709b35b1aabbee717b973c3e40699e235
  - 0ef94f95be3ea5c0b8ac981cc39d78e9a84577a7
  - c732c9b49f323937dda5ca4b5fb3b50661d49b2f
  - 61250c26dbdfde4f7a6e9988d131bbdfe10a171c
  - 5c3d2be092cf02510eda288ab507649bf6b858ec
  - b7b69bc4d35d55212f575a24864ff17c4234d87d
  - cd1192a37627ee719bad66275a31dbb971afc039
  - 093c1e9863e4c04ce6b8403887caa726eaae8f9b
  - 15c4c7fc8e7cdafe5d18afcc4eda37bc464694f3
  - 1c6167176e6aad2cad0d72f07ac8e720a6b4f12a
  - f22b9e71446043818c3ffc5737beec41a4f9e40e
  - this_handoff_commit
files_changed:
  - .github/workflows/prompt-05.yml
  - contracts/locks/builder-to-responsive-transition.v1.lock.json
  - contracts/locks/final-gate.v1.lock.json
  - docs/BEHAVIORAL_RULE_COVERAGE.md
  - docs/DIAGNOSTIC_CODES.md
  - docs/IMPLEMENTATION_STATUS.yaml
  - docs/STATUS_DECISION_MATRIX.md
  - docs/TRANSITION_BOUNDARY_MAP.md
  - docs/handoffs/PROMPT-05_HANDOFF.md
  - schemas/builder-to-responsive-transition-result/builder-to-responsive-transition-result.v1.schema.json
  - schemas/final-gate-result/final-gate-result.v1.schema.json
  - scripts/compute-builder-to-responsive-lock.py
  - scripts/compute-final-gate-lock.py
  - src/ev4_transition/progress.py
  - src/ev4_transition/transitions/__init__.py
  - src/ev4_transition/transitions/builder_to_responsive.py
  - src/ev4_transition/transitions/final_gate.py
  - tests/fixture_matrix/builder_to_responsive/invalid/forbidden_claim.invalid.json
  - tests/fixture_matrix/builder_to_responsive/invalid/missing_mobile_evidence.invalid.json
  - tests/fixture_matrix/builder_to_responsive/valid/builder_responsive_input.valid.json
  - tests/transitions/test_builder_to_responsive.py
  - tests/transitions/test_final_gate.py
tests_run:
  - python -m py_compile for 7 new/changed Prompt-05 Python files in sandbox
  - JSON parse checks for 7 Prompt-05 JSON files in sandbox
  - pytest tests/transitions/test_builder_to_responsive.py::test_builder_to_responsive_missing_builder_evidence_is_insufficient_evidence in sandbox mini-checkout
  - pytest tests/transitions/test_final_gate.py::test_final_gate_blocks_production_ready_without_evidence in sandbox mini-checkout
tests_passed:
  - python_syntax_checks_passed_7_files
  - json_parse_checks_passed_7_files
  - selected_pytest_b2r_missing_builder_evidence_passed
  - selected_pytest_final_gate_forbidden_production_ready_passed
tests_failed:
  - full_prompt_05_pytest_in_sandbox_timed_out_before_completion
tests_not_run:
  - full repository pytest on a real checkout
  - GitHub Actions branch CI after PR creation
  - exact owner lock/hash verification against Builder and Responsive checkouts
  - live Responsive input boundary validator smoke against a real owner checkout
  - live Responsive output validator smoke against a real owner checkout
coverage_rules_advanced:
  - PG-DOWNSTREAM-001 remains fixture_tested; downstream_contract_enforced is not claimed
  - PG-EVIDENCE-001 fixture_tested baseline for missing Builder evidence, viewport evidence, and final real evidence
  - PG-SYNTH-001 fixture_tested baseline for synthetic/raw screenshot limits
  - PG-HASH-001 validator_backed baseline for B2R/final lock verification functions
  - PG-VALIDATOR-001 fixture_tested baseline for missing Responsive schema/validator fail-closed behavior
  - PG-OUTPUT-001 fixture_tested baseline for B2R/final result schema validation
coverage_rules_still_gap:
  - PG-HASH-001 is not ci_enforced until exact owner hashes are refreshed and CI verifies them
  - PG-DOWNSTREAM-001 is not downstream_contract_enforced
  - real Builder execution evidence is unavailable
  - real Responsive output evidence is unavailable
new_diagnostics:
  - PG.B2R.LOCK_NOT_OBJECT
  - PG.B2R.LOCK_VERSION_MISMATCH
  - PG.B2R.LOCK_TRANSITION_ID_MISMATCH
  - PG.B2R.LOCK_FILES_NOT_ARRAY
  - PG.B2R.LOCK_ENTRY_NOT_OBJECT
  - PG.B2R.LOCK_ROLE_UNEXPECTED
  - PG.B2R.LOCK_ROLE_DUPLICATE
  - PG.B2R.LOCK_ROLE_MISSING
  - PG.B2R.LOCK_REPOSITORY_MISMATCH
  - PG.B2R.LOCK_COMMIT_MISMATCH
  - PG.B2R.LOCK_PATH_MISMATCH
  - PG.B2R.LOCK_IDENTITY_MISMATCH
  - PG.B2R.OWNER_FILE_READ_FAILED
  - PG.B2R.EXTERNAL_HASH_MISMATCH
  - PG.B2R.EXTERNAL_IDENTITY_MISMATCH
  - PG.B2R.INPUT_NOT_OBJECT
  - PG.B2R.RESPONSIVE_INPUT_MISSING
  - PG.B2R.RESPONSIVE_SCHEMA_UNAVAILABLE
  - PG.B2R.RESPONSIVE_SCHEMA_VALIDATION_FAILED
  - PG.B2R.RESPONSIVE_VALIDATOR_MISSING
  - PG.B2R.RESPONSIVE_VALIDATOR_FAILED
  - PG.B2R.BUILDER_EVIDENCE_MISSING
  - PG.B2R.VIEWPORT_EVIDENCE_MISSING
  - PG.B2R.RAW_SCREENSHOT_CORRECTNESS_CLAIM
  - PG.B2R.CI_FRONTEND_CORRECTNESS_CLAIM
  - PG.B2R.FORBIDDEN_CLAIM
  - PG.B2R.SYNTHETIC_ONLY_EVIDENCE
  - PG.B2R.ACCEPTED_REQUIRES_MISSING
  - PG.FINAL.LOCK_NOT_OBJECT
  - PG.FINAL.LOCK_VERSION_MISMATCH
  - PG.FINAL.LOCK_TRANSITION_ID_MISMATCH
  - PG.FINAL.LOCK_FILES_NOT_ARRAY
  - PG.FINAL.LOCK_ENTRY_NOT_OBJECT
  - PG.FINAL.LOCK_ROLE_UNEXPECTED
  - PG.FINAL.LOCK_ROLE_MISSING
  - PG.FINAL.LOCK_REPOSITORY_MISMATCH
  - PG.FINAL.LOCK_COMMIT_MISMATCH
  - PG.FINAL.LOCK_PATH_MISMATCH
  - PG.FINAL.LOCK_IDENTITY_MISMATCH
  - PG.FINAL.OWNER_FILE_READ_FAILED
  - PG.FINAL.EXTERNAL_HASH_MISMATCH
  - PG.FINAL.EXTERNAL_IDENTITY_MISMATCH
  - PG.FINAL.INPUT_NOT_OBJECT
  - PG.FINAL.RESPONSIVE_OUTPUT_MISSING
  - PG.FINAL.RESPONSIVE_SCHEMA_UNAVAILABLE
  - PG.FINAL.RESPONSIVE_SCHEMA_VALIDATION_FAILED
  - PG.FINAL.RESPONSIVE_VALIDATOR_MISSING
  - PG.FINAL.RESPONSIVE_VALIDATOR_FAILED
  - PG.FINAL.REAL_EVIDENCE_MISSING
  - PG.FINAL.SYNTHETIC_ONLY_EVIDENCE
  - PG.FINAL.FORBIDDEN_CLAIM
  - PG.FINAL.CI_FRONTEND_CORRECTNESS_CLAIM
  - PG.FINAL.ACCEPTED_REQUIRES_MISSING
new_or_changed_cli:
  - scripts/compute-builder-to-responsive-lock.py
  - scripts/compute-final-gate-lock.py
new_or_changed_ci:
  - .github/workflows/prompt-05.yml
important_design_decisions:
  - Project Gate does not create or copy a Responsive-owned input schema.
  - Responsive schema/validator absence maps to insufficient_evidence.
  - Forbidden readiness/correctness claims map to invalid.
  - CI success and raw screenshots are explicitly not frontend/responsive correctness evidence.
  - Final Gate requires real non-synthetic evidence and prior lock-chain verification.
  - Lock manifests use honest placeholders until exact owner file-byte hashes are refreshed.
web_sources_used: []
next_allowed_prompt: prompt_05_lock_refresh_and_ci_stabilization
blocking_issues:
  - exact Prompt-05 lock hashes are not refreshed from owner checkouts
  - full repo pytest was not executed locally because public git clone failed in sandbox with DNS resolution failure
  - branch GitHub Actions status is pending until PR/push workflow execution is observed
remaining_insufficient_evidence:
  - prompt_05_exact_owner_file_byte_hash_refresh
  - prompt_05_branch_ci_green_on_latest_head
  - real_non_synthetic_CE_to_Builder_transition_evidence
  - real_Builder_execution_evidence_bundle
  - real_Responsive_output_evidence_bundle
  - downstream_rejection_evidence_not_claimed
