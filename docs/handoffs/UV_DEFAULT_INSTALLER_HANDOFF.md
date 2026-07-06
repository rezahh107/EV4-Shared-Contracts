# UV Default Installer Handoff

## Branch

`codex/make-uv-the-default-installer`

## PR URL

`https://github.com/rezahh107/EV4-Project-Gate/pull/33`

## Commits

Original uv migration commits are recorded in PR history. CI repair follow-up commits added after PR review:

- `67033295dc91c26be27b50efc250ec687ced0375` — `Fix Prompt 05 owner validator Python environment`
- `688768d66bcac58612c3d23e56c81587c20b8d18` — `Fix Skeleton Health owner validator Python environment`
- `2af91baa5ac7c9db4a914b5eefeef93af0f821d4` — `Update uv owner-validator regression coverage`
- Current handoff update commit: see branch history / final repair report.

## Required change versus optional recommendation

Required: make `uv` the default local and CI Python installer/environment workflow while preserving a secondary `pip` fallback.

Optional recommendation: continue using `setuptools` and `[project.optional-dependencies]`; no migration to `[dependency-groups]` was needed.

## Repositories and contract boundaries affected

- Primary repository: `rezahh107/EV4-Project-Gate`.
- Specialist repository schemas, validators, adapters, fixtures, and transition semantics were not changed.
- Official specialist validators are still executed from their owner repository working directories.
- The CI repair only changes the Python interpreter used to run those owner scripts: Project Gate's `uv sync` creates `.venv`, and the owner scripts are invoked with `${{ github.workspace }}/EV4-Project-Gate/.venv/bin/python` so required Python dependencies such as `jsonschema` are available.

## Official uv docs consulted

- Installation: `https://docs.astral.sh/uv/getting-started/installation/`
- Locking and syncing: `https://docs.astral.sh/uv/concepts/projects/sync/`
- Managing dependencies and extras: `https://docs.astral.sh/uv/concepts/projects/dependencies/`
- GitHub Actions: `https://docs.astral.sh/uv/guides/integration/github/`
- Python versions and `.python-version`: `https://docs.astral.sh/uv/concepts/python-versions/`

## uv version strategy

Local validation used `uv 0.7.22`. GitHub Actions install `astral-sh/setup-uv` pinned by full commit SHA and request `version: "0.7.22"` for lockfile consistency with the generated `uv.lock`.

## Python version policy

`pyproject.toml` remains `requires-python = ">=3.11"`. `.python-version` was added with `3.11` to select the default local interpreter for reproducible uv setup without raising the supported baseline.

## Dependency metadata decision

Kept `[project.optional-dependencies]` for `dev` and `ui`. They are documented as extras and synced with `uv sync --extra dev --extra ui`. They were not migrated to dependency groups because the existing metadata is valid project metadata and no dependency-group-only need was identified.

## Lockfile status

`uv.lock` was generated with `uv lock` and is committed in this PR.

## CI changes

Python-installing workflows now install uv via a full-SHA-pinned `astral-sh/setup-uv`, run `uv lock --check`, sync with `uv sync --locked --extra dev --extra ui`, and execute Project Gate Python tests/checks through `uv run` where changed.

Owner-validator CI steps are handled as a boundary case:

- `Prompt 05 / Run pinned official Responsive validators` runs inside `EV4-Responsive-Architect`, but uses Project Gate `.venv/bin/python`.
- `Skeleton Health / python-core / Official Architect validator fixture suite` runs inside `EV4-Architect-Repo`, but uses Project Gate `.venv/bin/python`.
- `Skeleton Health / python-core / Official CE validator fixture suite` runs inside `EV4-Constructability-Engineer-Repo`, but uses Project Gate `.venv/bin/python`.

This keeps the owner repository path boundary while avoiding the previous system-Python dependency gap.

## Docs updated

- `README.md`
- `docs/LOCAL_SETUP_GUIDE.md`
- `docs/PERSONAL_USE_GUIDE.md`
- `docs/E2E_DEMO_WORKFLOW.md`
- `docs/UI_OPERATOR_PANEL.md`
- `docs/VALIDATION_STRATEGY.md`
- `outputs/README.md`
- `examples/personal-use/README.md`
- `fixtures/personal-use/README.md`
- `docs/handoffs/UV_DEFAULT_INSTALLER_HANDOFF.md`

## Scripts added

- `scripts/setup-windows-uv.ps1`: safe Windows setup helper that refuses to auto-install uv and prints official install options if uv is missing.

## Regression coverage advanced

`tests/personal_use/test_personal_use_package.py` now checks that owner validator steps:

- keep the owner repository `working-directory`;
- define `PROJECT_GATE_PYTHON` as `${{ github.workspace }}/EV4-Project-Gate/.venv/bin/python`;
- invoke official owner scripts through `"$PROJECT_GATE_PYTHON"` instead of bare system `python`.

## Tests run before PR review

Author-reported/local validation from earlier PR work:

- `uv --version`
- `uv lock --check`
- `uv sync --locked --extra dev --extra ui`
- `uv run --locked pytest tests/personal_use tests/reporting/test_workflow_permissions.py tests/test_cli.py`
- `uv run --locked python scripts/check-github-action-pinning.py`
- `uv run --locked python scripts/check-workflow-permissions.py`
- `uv run --locked python scripts/check-capability-truth.py`
- `uv run --locked ev4-transition inspect`
- `uv run --locked python scripts/run-project-gate-demo.py --run-id uv-default-installer-smoke`
- `uv run --locked pytest`
- `npm run status`
- `npm run validate`

## Tests run during CI repair follow-up

No local test command was executed in this connector session after the CI repair commits. Live GitHub Actions logs were inspected, and the failing root cause was reproduced from the workflow job logs.

## Tests not run / still pending

- Native Windows execution of `scripts/setup-windows-uv.ps1` was not run.
- A local `uv run --locked pytest` pass was not run in this connector session.
- Remote GitHub Actions must rerun on the new PR head before CI success can be claimed.

## CI failure root cause fixed in follow-up

The reviewed head `02a832846fe3d56810f37961727dc6cab69a22fc` failed because official owner validators were launched with bare system `python`, while the required `jsonschema` dependency existed in the Project Gate uv-managed environment. The failing logs showed `ModuleNotFoundError: No module named 'jsonschema'` in both:

- `EV4-Responsive-Architect/validation/e2e/run_builder_responsive_input_boundary_check.py`
- `EV4-Architect-Repo/scripts/check-architect-stage-payload.py`

The repair invokes official owner scripts with Project Gate `.venv/bin/python` after `uv sync --locked --extra dev --extra ui` completes.

## Important design decision

Do not install dependencies separately inside every owner repository and do not edit owner repositories from this PR. Project Gate owns the CI orchestration environment for this PR, while owner repositories continue to own their validators and contracts.

## Rollback guidance

Revert the CI repair commits to restore the previous bare owner-validator `python` calls. Do not change transition locks or specialist contracts during rollback.

## Next safe action

Wait for GitHub Actions on the new PR head, then verify that `Prompt 05 Builder Responsive Final Gate`, `Skeleton Health`, `Prompt 06 Report UX`, and `UI Runtime Smoke` all pass before merge consideration.

## Remaining gaps

- CI success on the new head is not yet evidenced in this handoff.
- Native Windows script behavior still needs a Windows runner/user validation pass.
- Full `uv.lock` dependency audit remains outside this repair.
