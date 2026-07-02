# AGENTS.md

## Repository role

`EV4-Project-Gate` is the Stage Evidence protocol owner and deterministic Python transition engine for EV4 stage handoffs.

```text
EV4 stage output
        ↓
Project Gate validates evidence
        ↓
Project Gate runs deterministic transition
        ↓
Next stage receives JSON input package
```

## Runtime

```yaml
primary_runtime: python
package: ev4_transition
cli: ev4-transition
node_runtime: auxiliary_only
ui: not_implemented
```

Do not describe UI behavior as implemented. The upload → check → download model is the user workflow target; the current implementation is Python library + CLI.

## Read first

1. `README.md`
2. `docs/EV4_PROJECT_GATE_STATUS.md`
3. `schemas/README.md`
4. `transitions/*.json`
5. `src/ev4_transition/*`
6. `tests/*`
7. `.github/workflows/validate.yml`

Historical shared-contract promotion documents are not active architecture when they conflict with these files.

## Hard boundaries

Do not create a new repository, rename this repository, make Node the primary runtime, copy specialist schemas here as competing canonical domain schemas, invent evidence, silently normalize undocumented differences, or treat `insufficient_evidence` as a generic error.

## Python rules

- Use stable canonical JSON before hashing.
- Use SHA-256 over canonical UTF-8 JSON content.
- Keep transitions deterministic; do not inject live timestamps by default.
- Fail closed for missing, ambiguous, or unsupported transition rules.
- Preserve provenance from source bundles.
- Add tests for implemented rules.
- Keep synthetic fixtures clearly labeled.

## Validation

```bash
python -m pip install -e '.[dev]'
pytest
ev4-transition validate fixtures/valid/architect-stage-bundle.v1.json
ev4-transition transition fixtures/valid/architect-stage-bundle.v1.json --transition-id architect-to-ce.v1
ev4-transition validate fixtures/invalid/insufficient-evidence.v1.json --format persian
```
