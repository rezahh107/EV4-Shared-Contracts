prompt_id: PROMPT-04
branch: project-gate-prompt-04-ce-to-builder
pull_request: 20
base_branch: main
base_sha: 10e665cdec74ba5508042fa774a3934b16387192
handoff_refresh_context: after_PR_Inspector_YELLOW_repository_aware_lock_patch
pr_state: open_draft_unmerged

review_input:
  authoritative_review: PR_Inspector_v1_5_0_YELLOW_CHANGES_OR_VERIFICATION_REQUIRED
  uploaded_review_report: user_message_technical_handoff
  followup_blockers:
    - PRF-001: accepted_requires can misreport lock mismatch categories in invalid results
  non_blocking_findings:
    - PRF-002: committed status docs had stale CI evidence references

repository_aware_lock_patch:
  - Added repository, commit, and file_path details to PG.C2B.LOCK_ROLE_DUPLICATE.
  - Added repository, commit, and file_path details to PG.C2B.LOCK_REPOSITORY_MISMATCH, PG.C2B.LOCK_COMMIT_MISMATCH, PG.C2B.LOCK_PATH_MISMATCH, and PG.C2B.LOCK_IDENTITY_MISMATCH.
  - Added repository, commit, and file_path details to PG.C2B.EXTERNAL_IDENTITY_MISMATCH.
  - Added accepted_requires regression matrix for duplicate role, repository mismatch, commit mismatch, path mismatch, id mismatch, hash mismatch, and identity mismatch on both CE and Builder roles.

status_doc_refresh:
  - docs/BEHAVIORAL_RULE_COVERAGE.md no longer cites an old head/run as current evidence.
  - docs/IMPLEMENTATION_STATUS.yaml marks the repository-aware lock patch as pending CI rather than claiming older CI as current.
  - This handoff marks older green runs as historical and requires latest-head CI verification after this patch.

historical_green_before_repository_aware_patch:
  repository: rezahh107/EV4-Project-Gate
  workflow: Skeleton Health
  run_id: 28743697368
  checked_head_sha: d613dd21d644b18fad6eb869b7c229b4567e4ffa
  conclusion: success
  note: Historical evidence only; the repository-aware patch changes the PR head and requires a fresh CI result.

post_repository_aware_patch_validation_state:
  latest_head_sha: pending_after_this_handoff_commit
  github_actions_result: pending
  note: Re-run CI and PR Inspector review are required before merge.

files_changed_relevant_to_repository_aware_patch:
  - src/ev4_transition/transitions/ce_to_builder.py
  - tests/transitions/test_ce_to_builder.py
  - docs/BEHAVIORAL_RULE_COVERAGE.md
  - docs/IMPLEMENTATION_STATUS.yaml
  - docs/handoffs/PROMPT-04_HANDOFF.md

coverage_state:
  PG-C2B-001:
    behavioral_ledger_status: validator_backed
    ci_evidence: pending_after_repository_aware_patch
  PG-C2B-002:
    behavioral_ledger_status: validator_backed
    ci_evidence: pending_after_repository_aware_patch
  PG-DOWNSTREAM-001:
    behavioral_ledger_status: fixture_tested
    downstream_contract_enforced: false

important_design_decisions:
  - PR #20 stayed draft and was not merged.
  - accepted_requires still derives CE and Builder lock flags from repository-aware diagnostics.
  - Diagnostics were made repository-aware instead of adding a separate classifier, preserving the existing result contract.
  - C2B live smoke remains integration evidence, not real non-synthetic handoff evidence.

web_sources_used: []

remaining_insufficient_evidence:
  - post_repository_aware_patch_green_ci_on_latest_head
  - real_non_synthetic_CE_to_Builder_transition_evidence
  - Builder_to_Responsive_Project_Gate_transition
  - final_evidence_gate

next_allowed_prompt: verify_CI_and_PR_Inspector_review_on_latest_head
