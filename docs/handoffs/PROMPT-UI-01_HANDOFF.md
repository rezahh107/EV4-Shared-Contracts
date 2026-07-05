# PROMPT-UI-01 Handoff — Local Operator Panel

```yaml
prompt: UI operator panel prompt 1 of 3
branch: ui/operator-panel
pull_request: 28
head_sha: 68055db677a2f2a10af0a4d4c1f5c4a3782d7a59
scope: local Persian-first operator UI shell
status: verified_by_pr_ci
```

## Branch

- `ui/operator-panel`

## Pull request

- PR: `#28` — `Add local Project Gate operator UI`
- Base: `main`
- Head: `ui/operator-panel`

## Commits

- Branch is `16` commits ahead of `main` at handoff update time.
- Final head verified by CI: `68055db677a2f2a10af0a4d4c1f5c4a3782d7a59`.

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

## Capability truth change rationale

`src/ev4_transition/data/capability-status.v1.json`, `docs/IMPLEMENTATION_STATUS.yaml`, `README.md`, and `AGENTS.md` were updated because the active capability source previously said `user_interface.status: not_implemented`. Leaving that value unchanged after adding the operator UI shell would create active-doc drift and a false status claim. The new value is limited to `implemented_initial_operator_panel` and does not claim service-layer wiring for all transitions.

## Coverage rules advanced

| Rule | Status |
|---|---|
| malformed JSON safe error | ci_enforced |
| status mapping for accepted/invalid/insufficient_evidence/repair_needed | ci_enforced |
| diagnostics preserve code/severity/path | ci_enforced |
| LTR isolation for technical tokens | ci_enforced |
| capability inspector read-only | ci_enforced |
| unavailable transitions do not fake execution | ci_enforced |
| report/result rendering does not mutate result object | ci_enforced |

## Coverage rules still gap

| Rule | Gap |
|---|---|
| browser-level UI accessibility | not validated by browser automation |
| CE→Builder UI execution | pending Prompt 2 service-layer integration |
| Builder→Responsive UI execution | pending Prompt 2 service-layer integration |
| Final Evidence Gate UI execution | pending Prompt 2 service-layer integration |
| packaging/user run polish | pending Prompt 3 |

## New diagnostics

- `MALFORMED_JSON`
- `UI_INPUT_REQUIRED`
- `UI_TRANSITION_NOT_WIRED`
- `UI_LOCAL_PATH_REQUIRED`
- `UI_LOCAL_PATH_NOT_URL`
- `UI_LOCAL_PATH_NOT_FOUND`
- `LOCAL_PATH_READ_ERROR`
- `TRANSITION_RESULT_SCHEMA_VALIDATION_FAILED`

## CLI / CI changes

- Added optional local UI entry point: `ev4-project-gate-ui`.
- Did not expose new public Project Gate transition commands.
- Added `Operator UI adapter tests` step to `.github/workflows/validate.yml` because otherwise the new UI tests would not be CI-enforced.

## Tests run

Local/container attempt:

```bash
git clone --branch ui/operator-panel --single-branch https://github.com/rezahh107/EV4-Project-Gate.git /tmp/EV4-Project-Gate-ui
```

Result: failed because the execution container could not resolve `github.com`.

GitHub Actions on PR `#28`, head `68055db677a2f2a10af0a4d4c1f5c4a3782d7a59`:

- `Skeleton Health` run `28757902985`: success.
- `Prompt 05 Builder Responsive Final Gate` run `28757902962`: success.
- `Prompt 06 Report UX` run `28757902964`: success.

Confirmed successful CI steps include:

- `Operator UI adapter tests`
- `Verify capability truth`
- `Verify workflow permissions`
- `Run skeleton status`
- `Run skeleton validation`
- `CLI and bundle tests`
- `Behavioral coverage validator`
- `Behavioral fixture validation`
- `CLI smoke valid bundle`
- `CLI smoke invalid array`
- `CLI smoke Persian insufficient evidence`

## Tests not run

- Browser-driven Gradio UI testing was not run.
- Manual visual inspection of the live UI was not performed in this prompt.

## Important design decisions

- UI event handlers delegate to `ui.adapters` and do not contain transition business logic.
- The UI uses direct Python calls rather than subprocess CLI calls.
- Only `Validate Stage Evidence Bundle`, `Architect → CE`, and `Inspect Capabilities` are wired.
- CE→Builder, Builder→Responsive, and Final Evidence Gate show `insufficient_evidence` / not wired rather than fake execution.
- Reports reuse `src/ev4_transition/reports/` renderers.
- Result objects are deep-copied before report rendering.

## Web sources used

- None. The implementation followed live repository files and uploaded Project rules.

## Next allowed prompt

- Prompt 2: service-layer integration for currently unwired UI transitions.

## Blockers

- No browser-level UI run evidence yet.
- No merge to `main`; PR remains open.

## Remaining insufficient_evidence

- real non-synthetic CE→Builder handoff evidence
- real Builder execution evidence bundle
- real Responsive input/output evidence bundle
- accessibility/export/frontend correctness evidence
- downstream owner rejection evidence for downstream-contract-enforced claims
