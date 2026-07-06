# PROMPT-UI-01 Handoff — Local Operator Panel

```yaml
prompt: UI operator panel prompt 1 of 3
repair_prompt: UI operator panel repair
branch: ui/operator-panel
pull_request: 28
head_before_repair: 5442b5e34bc6f70703b2e99689e0ee56fafec7b5
head_after_repair: pending_final_ci_head
scope: local Persian-first operator UI shell
status: repair_applied_pending_final_ci
service_integration_status: pending
```

## Branch

- `ui/operator-panel`

## Pull request

- PR: `#28` — `Add local Project Gate operator UI`
- Base: `main`
- Head: `ui/operator-panel`

## Commits

- Branch was `17` commits ahead of `main` before the repair.
- Repair commits added focused changes for dependency scope, UI input guard rails, docs, and tests.
- Final head and CI evidence must be read from PR checks after this handoff update.

## Files changed

- `.github/workflows/validate.yml`
- `src/ev4_transition/ui/__init__.py`
- `src/ev4_transition/ui/app.py`
- `src/ev4_transition/ui/state.py`
- `src/ev4_transition/ui/adapters.py`
- `src/ev4_transition/ui/components.py`
- `tests/ui/test_operator_panel.py`
- `docs/UI_OPERATOR_PANEL.md`
- `docs/UI_UX_TRACEABILITY.md`
- `docs/handoffs/PROMPT-UI-01_HANDOFF.md`
- `pyproject.toml`
- `README.md`
- `AGENTS.md`
- `docs/IMPLEMENTATION_STATUS.yaml`
- `src/ev4_transition/data/capability-status.v1.json`

## Scope implemented

- Added local Gradio operator panel composition in `src/ev4_transition/ui/app.py`.
- Added UI-safe adapter boundary in `src/ev4_transition/ui/adapters.py`.
- Added Persian status summary, diagnostics rows, capability rows, and LTR-isolation helpers.
- Added JSON upload/paste support with malformed JSON fail-closed behavior.
- Added local path guards for repository checkout paths.
- Added read-only capability inspector.
- Added downloadable `result.json`, `report.md`, and `report.html` generation through existing report renderers.
- Added tests for UI helper/adapter behavior.
- Added CI execution for `pytest tests/ui` in `Skeleton Health`.

## Repair changes

- Removed `gradio>=4,<6` from mandatory `[project].dependencies`.
- Kept `gradio>=4,<6` under `[project.optional-dependencies].ui`.
- Kept `ev4-project-gate-ui` entry point; `src/ev4_transition/ui/app.py` fails clearly if `gradio` is missing.
- Updated UI install docs to use `python -m pip install -e '.[dev,ui]'`.
- Added fail-closed `UI_INPUT_INVALID_TYPE` for JSON values that are valid JSON but not objects.
- Added fail-closed `UI_PROJECT_GATE_SCHEMA_ROOT_INVALID` when the Project Gate root lacks the expected `schemas/stage-bundle/stage-bundle.v1.schema.json` file.
- Made `ltr_token(...)` return `""` for `None` and stringify non-string values before LTR isolation.
- Expanded `tests/ui/test_operator_panel.py` for the repair cases.

## Not changed

- Transition engine semantics.
- Official specialist validators/adapters.
- Lock manifests.
- Specialist schemas.
- Transition result schemas.
- CE constructability logic.
- Builder runtime logic.
- Responsive repair logic.
- Public CLI transition exposure.
- Production/readiness claims.
- Service-layer files from PR `#29`.

## Capability truth change rationale

`src/ev4_transition/data/capability-status.v1.json`, `docs/IMPLEMENTATION_STATUS.yaml`, `README.md`, and `AGENTS.md` were updated in the original UI prompt because the active capability source previously said `user_interface.status: not_implemented`. The value is limited to `implemented_initial_operator_panel` and does not claim service-layer wiring for all transitions.

## Coverage rules advanced

| Rule | Status |
|---|---|
| malformed JSON safe error | ci_enforced |
| non-object JSON safe error | fixture_tested_pending_final_ci |
| missing Project Gate schemas root safe error | fixture_tested_pending_final_ci |
| status mapping for accepted/invalid/insufficient_evidence/repair_needed | ci_enforced |
| diagnostics preserve code/severity/path | ci_enforced |
| LTR isolation and None-safe technical tokens | fixture_tested_pending_final_ci |
| capability inspector read-only | ci_enforced |
| unavailable transitions do not fake execution or return accepted | fixture_tested_pending_final_ci |
| report/result rendering does not mutate result object | ci_enforced |
| Gradio remains optional UI extra | fixture_tested_pending_final_ci |

## Coverage rules still gap

| Rule | Gap |
|---|---|
| browser-level UI accessibility | not validated by browser automation |
| CE→Builder UI execution | pending service-layer integration after PR #29 path is intentionally adopted |
| Builder→Responsive UI execution | pending service-layer integration after PR #29 path is intentionally adopted |
| Final Evidence Gate UI execution | pending service-layer integration after PR #29 path is intentionally adopted |
| packaging/user run polish | pending Prompt 3 |

## New diagnostics

- `MALFORMED_JSON`
- `UI_INPUT_REQUIRED`
- `UI_INPUT_INVALID_TYPE`
- `UI_TRANSITION_NOT_WIRED`
- `UI_PROJECT_GATE_SCHEMA_ROOT_INVALID`
- `UI_LOCAL_PATH_REQUIRED`
- `UI_LOCAL_PATH_NOT_URL`
- `UI_LOCAL_PATH_NOT_FOUND`
- `LOCAL_PATH_READ_ERROR`
- `TRANSITION_RESULT_SCHEMA_VALIDATION_FAILED`

## CLI / CI changes

- Added optional local UI entry point: `ev4-project-gate-ui`.
- Did not expose new public Project Gate transition commands.
- Added `Operator UI adapter tests` step to `.github/workflows/validate.yml` because otherwise the new UI tests would not be CI-enforced.
- No further workflow rewrite was performed in the repair.

## Tests run

Local/container attempt from the original UI prompt:

```bash
git clone --branch ui/operator-panel --single-branch https://github.com/rezahh107/EV4-Project-Gate.git /tmp/EV4-Project-Gate-ui
```

Result: failed because the execution container could not resolve `github.com`.

GitHub Actions before repair, PR `#28`, head `68055db677a2f2a10af0a4d4c1f5c4a3782d7a59`:

- `Skeleton Health` run `28757902985`: success.
- `Prompt 05 Builder Responsive Final Gate` run `28757902962`: success.
- `Prompt 06 Report UX` run `28757902964`: success.

Repair validation pending after this handoff update:

- `Skeleton Health` must pass on final repair head.
- `Prompt 05 Builder Responsive Final Gate` must pass on final repair head.
- `Prompt 06 Report UX` must pass on final repair head.

## Tests not run

- Browser-driven Gradio UI testing was not run.
- Manual visual inspection of the live UI was not performed.
- Optional UI launch command `python -m ev4_transition.ui.app` was not executed in this environment.
- `python -m pip install -e '.[dev,ui]'` was not executed in this environment.

## Important design decisions

- UI event handlers delegate to `ui.adapters` and do not contain transition business logic.
- The UI uses direct Python calls rather than subprocess CLI calls.
- Only `Validate Stage Evidence Bundle`, `Architect → CE`, and `Inspect Capabilities` are wired.
- CE→Builder, Builder→Responsive, and Final Evidence Gate remain `insufficient_evidence` / not wired in this repair.
- PR `#29` was inspected only for service contract compatibility context; no service files were modified here.
- Reports reuse `src/ev4_transition/reports/` renderers.
- Result objects are deep-copied before report rendering.

## Web sources used

- None. The implementation followed live repository files, PR review comments, PR `#29` service contract context, and uploaded Project rules.

## Next allowed prompt

- Service-layer adoption/integration after PR `#29` is intentionally available to this branch.

## Blockers

- No browser-level UI run evidence yet.
- No merge to `main`; PR remains open.

## Remaining insufficient_evidence

- real non-synthetic CE→Builder handoff evidence
- real Builder execution evidence bundle
- real Responsive input/output evidence bundle
- accessibility/export/frontend correctness evidence
- downstream owner rejection evidence for downstream-contract-enforced claims
