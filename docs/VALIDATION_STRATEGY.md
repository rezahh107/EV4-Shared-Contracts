# EV4 Project Gate Validation Strategy

Project Gate validation has two layers:

1. Schema validation for the Stage Evidence bundle envelope.
2. Transition-specific evidence validation before producing the next-stage input package.

If a bundle is structurally valid but lacks required evidence, the result is:

```yaml
status: insufficient_evidence
```

This is not a generic failure. It means the engine has enough structure to understand the bundle but not enough evidence to safely transition.

## Commands

```bash
python -m pip install -e '.[dev]'
pytest
ev4-transition validate fixtures/valid/architect-stage-bundle.v1.json
ev4-transition transition fixtures/valid/architect-stage-bundle.v1.json --transition-id architect-to-ce.v1
ev4-transition validate fixtures/invalid/insufficient-evidence.v1.json --format persian
```
