# PROMPT-UI-01 Handoff — Local Operator Panel

```yaml
prompt: UI operator panel prompt 1 of 3
branch: ui/operator-panel
scope: local Persian-first operator UI shell
status: implemented_on_branch_pending_validation_and_ci
```

## Branch

- `ui/operator-panel`

## Commits

Created on branch through the GitHub connector. Final commit list should be verified from the PR before merge.

## Files changed

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
| malformed JSON safe error | fixture_tested |
| status mapping for accepted/invalid/insufficient_evidence/repair_needed | fixture_tested |
| diagnostics preserve code/severity/path | fixture_tested |
| LTR isolation for technical tokens | fixture_tested |
| capability inspector read-only | fixture_tested |
| unavailable transitions do not fake execution | fixture_tested |
| report/result rendering does not mutate result object | fixture_tested |

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
- Did not modify GitHub Actions workflows.

## Tests run

Validation commands are recorded in the final PR/report after execution. At handoff creation time, local validation had not yet been completed.

## Tests not run yet

- `python -m pip install -e '.[dev]'`
- `pytest tests/ui`
- `pytest`
- `python scripts/check-capability-truth.py`
- `python scripts/check-workflow-permissions.py`
- `npm run status`
- `npm run validate`

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
- No GitHub Actions CI result yet for this branch at handoff creation time.

## Remaining insufficient_evidence

- real non-synthetic CE→Builder handoff evidence
- real Builder execution evidence bundle
- real Responsive input/output evidence bundle
- accessibility/export/frontend correctness evidence
- downstream owner rejection evidence for downstream-contract-enforced claims
