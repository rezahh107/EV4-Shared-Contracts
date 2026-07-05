prompt_id: PROMPT-04
branch: project-gate-prompt-04-ce-to-builder
pull_request: 20
base_branch: main
base_sha: 10e665cdec74ba5508042fa774a3934b16387192
handoff_refresh_context: after_PR_Inspector_RED_followup_patch
pr_state: open_draft_unmerged

review_input:
  authoritative_review: PR_Inspector_v1_5_0_RED_DO_NOT_MERGE
  uploaded_review_report: /mnt/data/Pasted text.txt
  followup_blockers:
    - PRF-001: workflow uses mutable GitHub Action tags
    - PRF-002: raw/no-source CE package could satisfy required_evidence_present
    - PRF-003: C2B coverage/status docs had inconsistent ci_enforced claims

followup_fixes:
  - PRF-001: .github/workflows/validate.yml pins actions/checkout, actions/setup-node, actions/setup-python, and actions/upload-artifact to full 40-character commit SHAs.
  - PRF-001: scripts/check-github-action-pinning.py added and passed in CI.
  - PRF-002: CE→Builder transition emits PG.C2B.REAL_EVIDENCE_REQUIRED when require_real_evidence=True and input is a raw/no-source CE package.
  - PRF-002: tests/transitions/test_ce_to_builder.py has a direct negative test for raw/no-source input with require_real_evidence=True.
  - PRF-003: handoff/status docs separate CI evidence from behavioral ledger status; C2B remains validator_backed in behavioral coverage until fixture-bound promotion.

confirmed_followup_green_ci:
  repository: rezahh107/EV4-Project-Gate
  workflow: Skeleton Health
  run_id: 28743548242
  run_number: 359
  checked_head_sha: 9ca2bbdbd6448e13ce49ee6dac532449808444ce
  conclusion: success
  jobs:
    skeleton: success
    python-core: success
  important_steps:
    Verify GitHub Action pins: success
    CE-to-Builder transition pytest: success
    Behavioral coverage validator: success
    CE-to-Builder lock verification: success
    CE-to-Builder live owner tool smoke: success
  note: Recheck the current PR head before merge if new commits are added after this handoff refresh.

files_changed_relevant_to_followup:
  - .github/workflows/validate.yml
  - scripts/check-github-action-pinning.py
  - src/ev4_transition/transitions/ce_to_builder.py
  - tests/transitions/test_ce_to_builder.py
  - docs/DIAGNOSTIC_CODES.md
  - docs/IMPLEMENTATION_STATUS.yaml
  - docs/handoffs/PROMPT-04_HANDOFF.md

coverage_state:
  PG-C2B-001:
    behavioral_ledger_status: validator_backed
    ci_evidence: CE-to-Builder lock verification passed in run 28743548242
  PG-C2B-002:
    behavioral_ledger_status: validator_backed
    ci_evidence: CE-to-Builder live owner smoke passed in run 28743548242
  PG-DOWNSTREAM-001:
    behavioral_ledger_status: fixture_tested
    downstream_contract_enforced: false

important_design_decisions:
  - PR #20 stayed draft and was not merged.
  - Immutable GitHub Action SHAs were resolved from current action tag commits with GitHub connector compare evidence.
  - The static action-pinning guard checks the affected workflow by default and can check all workflow files with --all-workflows.
  - Real evidence remains stricter than integration smoke: raw CE package input is allowed only when require_real_evidence=False.
  - C2B live smoke still uses an owner fixture and remains integration evidence, not real non-synthetic handoff evidence.

web_sources_used: []

remaining_insufficient_evidence:
  - real_non_synthetic_CE_to_Builder_transition_evidence
  - Builder_to_Responsive_Project_Gate_transition
  - final_evidence_gate

next_allowed_prompt: PR_Inspector_review_on_latest_head
