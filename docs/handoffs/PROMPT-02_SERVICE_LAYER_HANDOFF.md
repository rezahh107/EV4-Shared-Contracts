# PROMPT-02 Service Layer Handoff

```yaml
prompt_id: PROMPT-02-service-layer
branch: feature/gate-service-api
status: implementation_attempted_with_connector
scope: internal_python_service_api_for_future_operator_ui
```

## Branch

```text
feature/gate-service-api
```

Created from `main` through the GitHub connector.

## Commits

Commits are connector-created file commits on `feature/gate-service-api`. Exact final head SHA must be read from the PR/checks after creation.

## Files changed

```text
src/ev4_transition/service/__init__.py
src/ev4_transition/service/models.py
src/ev4_transition/service/json_input.py
src/ev4_transition/service/repo_paths.py
src/ev4_transition/service/capabilities.py
src/ev4_transition/service/dispatcher.py
src/ev4_transition/service/reports.py
tests/service/test_service_layer.py
docs/SERVICE_LAYER.md
docs/UI_SERVICE_CONTRACT.md
docs/handoffs/PROMPT-02_SERVICE_LAYER_HANDOFF.md
```

## Tests run

Local generated-file syntax checks in this ChatGPT container:

```text
python -m py_compile /mnt/data/service_patch/*.py
python -m py_compile /mnt/data/service_patch/tests_service/test_service_layer.py
```

Result:

```text
passed for generated service/test files only
```

## Tests not run

The following were requested but could not be run in this container because `git clone https://github.com/...` failed with DNS resolution error for `github.com`:

```text
python -m pip install -e '.[dev]'
pytest tests/service
pytest
python scripts/check-capability-truth.py
python scripts/check-workflow-permissions.py
npm run status
npm run validate
```

These must be verified by GitHub Actions or local checkout before merge.

## Coverage rules advanced

```yaml
service_json_input:
  status: fixture_tested
  notes: malformed, missing, and parsed-object copy behavior covered in tests/service
service_repo_paths:
  status: fixture_tested
  notes: missing required path and GitHub URL rejection covered
service_dispatcher:
  status: fixture_tested
  notes: transition dispatch boundaries monkeypatched to prove direct Python calls without CLI dependency
service_reports:
  status: fixture_tested
  notes: report generation immutability and progress-event hash exclusion covered
```

## Rules still gap

```yaml
ci_enforced_service_tests:
  status: prose_only
  reason: workflow was not changed in this patch
real_external_repo_execution:
  status: insufficient_evidence
  reason: no real local owner checkouts were available in this execution environment
operator_ui_integration:
  status: prose_only
  reason: Prompt 1 owns UI implementation
personal_packaging_examples:
  status: prose_only
  reason: Prompt 3 owns packaging, examples, run scripts, and demo workflow
```

## New diagnostics

```text
PG.SERVICE.JSON_INPUT_MISSING
PG.SERVICE.JSON_INPUT_AMBIGUOUS
PG.SERVICE.MALFORMED_JSON
PG.SERVICE.FILE_READ_ERROR
PG.SERVICE.REPO_PATH_MISSING
PG.SERVICE.REPO_PATH_NOT_LOCAL
PG.SERVICE.REPO_PATH_DOES_NOT_EXIST
PG.SERVICE.REPO_PATH_NOT_DIRECTORY
PG.SERVICE.TRANSITION_UNKNOWN
PG.SERVICE.RESULT_SCHEMA_VALIDATION_FAILED
PG.SERVICE.LOCAL_FILE_ACCESS_FAILED
PG.SERVICE.ENGINE_EXECUTION_FAILED
```

## CLI / CI changes

```yaml
public_cli_changes: none
ci_changes: none
```

No new public CLI transitions were exposed.

## Important design decisions

- Plain Python service API; no FastAPI, database, login, or cloud dependency.
- The UI calls `run_gate_request(...)` directly.
- `validate_bundle` uses `BundleValidator` directly.
- Transition choices call existing Python boundaries directly, not the public CLI.
- Missing local owner checkouts return `insufficient_evidence` before engine execution.
- JSON input is deep-copied and not mutated.
- Report generation deep-copies the engine result and uses existing Persian/RTL report renderers.
- Service status maps legacy `valid` to service-level `accepted`, while preserving the original engine result unchanged.

## Web sources used

```yaml
web_sources_used: []
```

No web research was needed; live repository files and uploaded Project rules were sufficient.

## Next allowed prompt

```text
Prompt 1: UI/operator panel may call this service API after PR review.
Prompt 3: packaging/examples/run scripts/demo workflow may add local launch wrappers after this service API is merged or rebased.
```

## Blockers

```yaml
local_full_test_execution: blocked_by_container_dns
ci_result_for_this_branch: unknown_until_pr_checks_complete
```

## Remaining insufficient_evidence

- real non-synthetic CE-to-Builder transition evidence
- real Builder execution evidence bundle
- real Responsive input/output evidence bundle
- accessibility/export/frontend correctness evidence
- downstream owner rejection evidence
- exact GitHub Actions result for this service branch until checks complete
