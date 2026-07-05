# PROMPT-03 Personal-Use E2E Package Handoff

```yaml
prompt_id: personal-use-parallel-prompt-03
branch: personal-use/e2e-package
pull_request: 27
handoff_status: pr_open_ci_green_on_repair_head
scope: personal-use packaging, local launchers, synthetic examples, output convention, controlled demo runner, packaging tests
head_sha: 03b7bcaa4990764f69fe7f69f9e58abc4d7c4bb2
```

## Commits

```text
71cc4136307be2751183a20c4a14ad91ab54be6d  Add local setup and demo package
03b7bcaa4990764f69fe7f69f9e58abc4d7c4bb2  Repair capability truth in README personal package
```

## Files changed

```text
README.md
.gitignore
docs/LOCAL_SETUP_GUIDE.md
docs/PERSONAL_USE_GUIDE.md
docs/E2E_DEMO_WORKFLOW.md
docs/handoffs/PROMPT-03_PERSONAL_USE_E2E_PACKAGE_HANDOFF.md
examples/personal-use/README.md
examples/personal-use/sample-valid-stage-bundle.synthetic.json
examples/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json
examples/personal-use/sample-malformed-json-note.md
fixtures/personal-use/README.md
fixtures/personal-use/sample-valid-stage-bundle.synthetic.json
fixtures/personal-use/sample-insufficient-evidence-stage-bundle.synthetic.json
fixtures/personal-use/sample-malformed-json-note.md
outputs/.gitkeep
outputs/README.md
scripts/run-project-gate-ui.py
scripts/run-project-gate-ui.ps1
scripts/run-project-gate-ui.bat
scripts/run-project-gate-demo.py
tests/personal_use/test_personal_use_package.py
tests/e2e/test_controlled_demo.py
```

## Coverage rules advanced

- Synthetic personal-use samples are explicitly labeled synthetic.
- Missing UI is handled as a clear user-facing setup gap rather than a traceback.
- Controlled demo keeps real evidence, real Elementor validation, and production readiness claims false.
- Generated output folder convention is documented and ignored under `outputs/runs/`.

## Rules still gap

- UI implementation remains owned by Prompt 1.
- Service/API integration remains owned by Prompt 2.
- Real non-synthetic EV4 evidence remains `insufficient_evidence`.
- These personal-use tests are added, but the explicit targeted local command `pytest tests/personal_use tests/e2e` was not run in this environment.

## New diagnostics / user-facing messages

- `UI is not installed yet. Merge Prompt 1 UI branch first.`
- Persian equivalent in `scripts/run-project-gate-ui.py`.
- Controlled demo report marks final gate status as `insufficient_evidence`.

## CLI / CI changes

- No public transition CLI was added.
- No transition semantics were changed.
- `.github/workflows/*` was intentionally not modified in this patch.

## Important design decisions

- Launcher discovers future UI modules but does not implement UI.
- Demo runner uses Project Gate bundle validation only and does not implement transition logic.
- Missing UI/service modules are reported as partial setup, not treated as real validation failure.
- Output files are organized under `outputs/runs/<timestamp-or-run-id>/`.
- README retained/restored the `Current Status` capability-truth YAML block required by `scripts/check-capability-truth.py`.

## Web sources used

None. Live repository files and uploaded Project rules were sufficient for this patch.

## Tests run

GitHub Actions on head `03b7bcaa4990764f69fe7f69f9e58abc4d7c4bb2`:

```text
Skeleton Health / run 28757886701 / success
Prompt 05 Builder Responsive Final Gate / run 28757886704 / success
Prompt 06 Report UX / run 28757886703 / success
```

## Tests not run

Not run locally in this ChatGPT environment because the container could not resolve `github.com` for a live clone and the GitHub connector does not provide a shell runner:

```bash
python -m pip install -e '.[dev]'
pytest tests/personal_use tests/e2e
pytest
python scripts/check-capability-truth.py
python scripts/check-workflow-permissions.py
npm run status
npm run validate
python scripts/run-project-gate-demo.py
```

## Next allowed prompt

Integration review after Prompt 1 UI branch and Prompt 2 service/API branch are merged.

## Blockers

- Prompt 1 UI files not present on inspected `main`.
- Prompt 2 service files not present on inspected `main`.
- Local shell validation not executed in this environment.

## Remaining `insufficient_evidence`

- real non-synthetic CE→Builder transition evidence
- real Builder execution evidence bundle
- real Responsive input/output evidence bundle
- accessibility/export/frontend correctness evidence
- downstream owner rejection evidence for downstream-contract-enforced claims
