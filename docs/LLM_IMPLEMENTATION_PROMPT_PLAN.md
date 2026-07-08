# LLM Implementation Prompt Plan

Status: active planning and progress-tracking artifact  
Created: 2026-07-08  
Repository: `rezahh107/EV4-Project-Gate`  
Current recommended next prompt: `Prompt 1 — Architecture Truth Reconciliation and Stage 0 Freeze`

## 1. Purpose

This file persists the approved multi-prompt implementation roadmap for `EV4-Project-Gate`.

It is a durable LLM handoff and progress-tracking document. Future LLM sessions and human maintainers should use it to:

1. understand the approved implementation sequence;
2. inspect the current repository state;
3. determine which prompts are complete, partial, blocked, superseded, or not started;
4. identify the next safe implementation prompt;
5. generate the next prompt or patch plan without reconstructing the whole architecture discussion from chat history.

This file exists because the repository must be developed through small, reviewable, evidence-bound patches rather than one large unreviewable rewrite.

## 2. Authority and Limits

This file is a planning and progress-control artifact.

It does **not** replace:

- `src/ev4_transition/data/capability-status.v1.json`;
- `docs/IMPLEMENTATION_STATUS.yaml`;
- `README.md`;
- `AGENTS.md`;
- active architecture, schema, lock, result, or transition contracts.

This file does not define actual capability truth. It records the approved implementation sequence and the evidence required before each prompt can be marked complete.

Update this file only when repository evidence supports the update.

Do not mark a prompt as `completed` because a model says it was completed. Completion requires repository evidence such as commits, PRs, tests, workflow runs, updated docs, or validated artifacts.

Do not use this file to upgrade implementation status, capability status, release readiness, real non-synthetic evidence, downstream enforcement, or production readiness.

## 3. Source Precedence

Future LLM sessions should use this precedence when determining repository state:

1. `src/ev4_transition/data/capability-status.v1.json` — canonical machine-readable capability truth.
2. `docs/IMPLEMENTATION_STATUS.yaml` — active status mirror and evidence ledger.
3. `AGENTS.md` — repository operating instructions for future LLM agents.
4. `README.md` — human-readable repository overview and command surface.
5. Active architecture and contract docs under `docs/`, especially:
   - `docs/ARCHITECTURE.md`
   - `docs/ROLE_BOUNDARY_MAP.md`
   - `docs/TRANSITION_BOUNDARY_MAP.md`
   - `docs/RESULT_MODEL.md`
   - `docs/STATUS_DECISION_MATRIX.md`
   - `docs/VALIDATION_STRATEGY.md`
   - `docs/BEHAVIORAL_RULE_COVERAGE.md`
   - `docs/REPORT_UX_CONTRACT.md`
6. Project Gate-owned schemas under `schemas/`.
7. Tests, fixtures, scripts, and GitHub workflows.
8. This file — staged implementation plan and prompt progress tracker.
9. Historical handoff files and previous chat notes.

When this file conflicts with higher-authority sources, follow the higher-authority source and update this file with evidence.

## 4. Current Recommended Execution Model

Use exactly ten implementation prompts unless a future approved architecture decision supersedes this plan.

Execution model:

```text
one branch per prompt
one pull request per prompt
one clear mission per prompt
one reviewable patch per prompt
```

Prompt 1 must happen first because the current architecture verdict is:

```text
NEEDS_DOC_RECONCILIATION
```

Every prompt must include:

- explicit scope;
- excluded scope;
- acceptance criteria;
- tests or evidence to collect;
- stop condition;
- final report;
- known limitations.

No prompt may implement unrelated later stages.

## 5. Status Values

Use only these prompt progress values:

```text
not_started
in_progress
partial
completed
blocked
superseded
```

Initial status is conservative. All prompts are `not_started` because this file records the approved future prompt sequence, not unrelated existing implementation already present in the repository.

If future evidence is uncertain, keep the prompt as `partial` or `blocked` and add a note. Do not mark it `completed` without evidence.

## 6. Prompt Roadmap Table

| Prompt # | Title | Roadmap Stage Covered | Objective | Files Likely Affected | Tests / Evidence | Stop Condition | Risk | Current Status | Notes |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | Architecture Truth Reconciliation and Stage 0 Freeze | Stage 0 — Architecture clarification | Reconcile active docs with current capability truth, remove or mark stale/conflicting UI/report/schema claims, define source precedence, and freeze the target architecture before code refactor. | `README.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/REPORT_UX_CONTRACT.md`, `docs/IMPLEMENTATION_STATUS.yaml`, `docs/ROLE_BOUNDARY_MAP.md`, `docs/VALIDATION_STRATEGY.md`, `schemas/README.md` | docs consistency check; capability truth check; evidence that stale UI/report/schema wording is resolved | Any active doc still conflicts with `capability-status.v1.json` or the architecture boundary. | Medium | not_started | Must be completed before code architecture patches. |
| 2 | Repository Structure Preparation | Stage 1 — Repository structure cleanup | Prepare future `domain/`, `validation/`, and `pipeline/` structure without changing public behavior. | `src/ev4_transition/domain/`, `src/ev4_transition/validation/`, `src/ev4_transition/pipeline/`, imports, architecture docs | full pytest or exact unrun limitation; CLI smoke; import compatibility evidence | Public CLI behavior changes or imports break without explicit approval. | Medium | not_started | Should be mostly additive and compatibility-preserving. |
| 3 | Core Domain Models and Schema Registry | Stage 2 — Core models and schemas | Define stable domain models and align the Project Gate-owned schema registry with actual owned schemas. | `domain/*`, `schemas/README.md`, `docs/RESULT_MODEL.md`, `docs/CONTRACT_INVENTORY.md`, schema registry docs/tests | schema registry tests; result schema validation; no copied specialist schemas | Any specialist-owned schema is copied or claimed as Project Gate canonical. | High | not_started | Must preserve specialist repository authority. |
| 4 | Layered Validation Engine | Stage 3 — Validation engine | Separate schema validation, semantic validation, evidence validation, lock validation, and result validation. | `validation/*`, `bundle_validator.py`, related tests and fixtures | valid/invalid/insufficient fixtures; deterministic diagnostic ordering; result schema validation | Status or diagnostic behavior changes accidentally or result validation stops being the final boundary. | High | not_started | Should preserve existing transition behavior unless explicitly documented. |
| 5 | Deterministic Pipeline Runner | Stage 4 — Pipeline runner | Introduce a central deterministic runner with explicit step sequencing and convert service dispatch into a thin router. | `pipeline/*`, `service/dispatcher.py`, transition modules, tests | service tests; transition tests; CLI smoke; pipeline step tests | CLI, service, and UI diverge in decision semantics. | High | not_started | Core pipeline must not depend on UI. |
| 6 | Reporting and Atomic Output Hardening | Stage 5 — Reporting outputs | Keep `result.json` canonical, make reporting non-mutating, and ensure success/download availability depends on completed atomic writes. | `reports/*`, `io/atomic_writer.py`, `ui/adapters.py`, `docs/REPORT_UX_CONTRACT.md`, reporting tests | report mutation tests; output failure tests; JSON/Markdown/HTML rendering evidence | Report layer changes status, adds diagnostics after validation, repairs evidence, or reports success for missing output. | High | not_started | UI download paths must not bypass output safety. |
| 7 | CLI / Service / UI Thin Interface Alignment | Stage 6 — CLI / API / UI integration | Ensure CLI, service, and local Gradio UI are thin interfaces over the same core runner and reporting layer. | `cli.py`, `service/*`, `ui/*`, operator docs/tests | CLI/service/UI parity tests; malformed JSON UI tests; local path preflight tests | UI can produce an acceptance path unavailable through CLI/core pipeline. | High | not_started | Do not add new UI features unless needed for parity. |
| 8 | CI Quality Gates Split and Hardening | Stage 7 — CI quality gates | Split and harden CI gates by real risk: core, contracts, transitions, behavioral coverage, UI smoke, docs truth. | `.github/workflows/*`, `scripts/check-*`, CI docs | workflow runs; action pinning; workflow permissions; lock checks; no stale generated output evidence | CI becomes friction-only or a gate lacks a documented risk. | Medium-High | not_started | Should happen after behavior is stable enough to protect. |
| 9 | Operator Documentation and Local-First Guide | Stage 8 — Documentation and operator guide | Add or update local operator guidance without overclaiming production, frontend, Elementor, export, accessibility, or responsive correctness. | `docs/OPERATOR_GUIDE.md`, `README.md`, `docs/PERSONAL_USE_GUIDE.md`, related docs | docs required-file check; no-readiness-claim scan; status wording review | Operator guide implies real readiness or hides `insufficient_evidence`. | Medium | not_started | Must remain Persian-friendly for user-facing explanations. |
| 10 | Regression and Compatibility Hardening | Stage 9 — Regression and compatibility hardening | Add regression tests and negative fixtures for historical failure modes and compatibility boundaries. | `tests/regression/`, `tests/behavioral_coverage/`, `docs/BEHAVIORAL_RULE_COVERAGE.md`, schemas/tests | regression tests; behavioral coverage validator; negative fixtures; CI evidence | Any Critical behavioral rule is promoted without invalid fixture and CI evidence. | High | not_started | Final hardening pass before broader adoption. |

## 7. Review Gates

### Prompt 1 Review Gate

Before moving to Prompt 2:

- docs consistency check passes;
- capability truth precedence is documented;
- UI/report contract conflict is resolved or explicitly marked historical;
- schema inventory no longer contains stale active claims;
- no new implementation claim is added without evidence.

### Prompt 2 Review Gate

Before moving to Prompt 3:

- existing CLI behavior is unchanged;
- imports remain backward compatible;
- no transition semantics changed;
- full tests pass, or any unrun tests are explicitly reported with reason.

### Prompt 3 Review Gate

Before moving to Prompt 4:

- schema registry matches actual Project Gate-owned schemas;
- no specialist repository schema is copied or claimed as Project Gate-owned;
- domain models are documented;
- existing result schemas still validate.

### Prompt 4 Review Gate

Before moving to Prompt 5:

- valid, invalid, and insufficient-evidence fixtures behave as before or intentional changes are documented;
- diagnostic ordering remains deterministic;
- result schema validation remains the final boundary;
- no evidence repair or silent normalization is introduced.

### Prompt 5 Review Gate

Before moving to Prompt 6:

- CLI and service use the same pipeline runner;
- transition sequencing is explicit;
- fail-closed behavior is preserved;
- no UI-specific logic exists inside pipeline core.

### Prompt 6 Review Gate

Before moving to Prompt 7:

- `result.json` remains canonical;
- reports do not mutate the engine result;
- atomic writing is used wherever success or download availability is claimed;
- Persian reports preserve RTL text and LTR-isolated technical fragments.

### Prompt 7 Review Gate

Before moving to Prompt 8:

- CLI, service, and UI parity is confirmed;
- UI remains a thin local client;
- malformed JSON and missing local paths fail safely;
- UI cannot convert `insufficient_evidence` into `accepted`.

### Prompt 8 Review Gate

Before moving to Prompt 9:

- CI gates map to real risks;
- workflow permissions remain least-privilege;
- GitHub Actions remain pinned according to repository policy;
- generated outputs are not stale;
- no duplicate friction-only gates are added.

### Prompt 9 Review Gate

Before moving to Prompt 10:

- operator guide explains local use without overclaiming readiness;
- status meanings are Persian-friendly and technically accurate;
- local checkout versus GitHub URL boundary is clear;
- user-facing wording preserves `insufficient_evidence` as warning/blocking.

### Prompt 10 Review Gate

Before considering the sequence complete:

- historical failure modes have regression tests;
- synthetic fixtures cannot unlock real readiness;
- `downstream_contract_enforced` cannot be claimed without downstream rejection evidence;
- legacy `valid` compatibility remains explicit or a migration ADR exists;
- behavioral coverage status promotions are evidence-backed.

## 8. Future Session Protocol

Before proposing any new implementation prompt, a future LLM session must:

1. read this file;
2. inspect the current repository state;
3. inspect the current branch and PR status if tools allow;
4. read `src/ev4_transition/data/capability-status.v1.json`;
5. read `docs/IMPLEMENTATION_STATUS.yaml`;
6. compare repository evidence against this file's acceptance criteria;
7. update the prompt status table only if evidence supports the update;
8. identify the next safe prompt;
9. refuse to skip blocked review gates;
10. avoid implementing unrelated stages;
11. report any uncertainty as `insufficient_evidence`, `partial`, or `blocked` rather than guessing.

A future LLM must not mark a prompt complete based only on chat memory, prose claims, or model self-report.

## 9. Progress Update Rules

After each prompt PR, update this file with an evidence-backed progress entry.

Each progress update must include:

```yaml
date: YYYY-MM-DD
prompt: number and title
branch: branch name
pull_request: PR number or null
commit_sha: exact commit SHA or null
tests_run:
  - command or workflow name
validation_result: pass | fail | not_run | insufficient_evidence
evidence:
  - file path, workflow run, artifact, or citation
resulting_status: not_started | in_progress | partial | completed | blocked | superseded
remaining_blockers:
  - item
next_prompt_recommendation: prompt number and title
```

Rules:

- If tests were not run, say `not_run` and explain why.
- If CI status is unavailable, use `insufficient_evidence`.
- If a PR only partially satisfies a prompt, mark the prompt `partial`, not `completed`.
- If a prompt is superseded by a later approved ADR, mark it `superseded` and cite the ADR.
- Do not update `capability-status.v1.json` from this file alone.

## 10. Progress Log

| Date | Prompt | Branch | PR | Commit SHA | Evidence | Resulting Status | Notes |
|---|---|---|---|---|---|---|---|
| 2026-07-08 | Plan persisted | `main` | null | null | `docs/LLM_IMPLEMENTATION_PROMPT_PLAN.md` created | not_started | Planning artifact created only. No implementation prompt executed. |

## 11. Next Recommended Action

Next recommended prompt:

```text
Prompt 1 — Architecture Truth Reconciliation and Stage 0 Freeze
```

Mission:

```text
Reconcile active repository documentation with current capability truth, remove or mark stale/conflicting UI/report/schema claims, define source precedence, and freeze the target architecture before any code refactor.
```

Initial Prompt 1 scope:

```text
README.md
AGENTS.md
docs/ARCHITECTURE.md
docs/REPORT_UX_CONTRACT.md
docs/IMPLEMENTATION_STATUS.yaml
docs/ROLE_BOUNDARY_MAP.md
docs/VALIDATION_STRATEGY.md
schemas/README.md
```

Prompt 1 must not:

```text
modify Python code
refactor src/ev4_transition
change CLI behavior
change UI behavior
change schemas
change CI workflows
implement later prompts
claim real non-synthetic readiness
promote behavioral coverage status without evidence
copy specialist schemas into Project Gate
```

## 12. Change Log

### 2026-07-08 — Create persistent 10-prompt implementation plan

- Added this file as the durable LLM handoff and progress tracker.
- Recorded the approved ten-prompt execution model.
- Set all prompt statuses to `not_started` conservatively.
- Set next recommended action to `Prompt 1 — Architecture Truth Reconciliation and Stage 0 Freeze`.
- No implementation prompt was executed.
