# EV4 Project Gate

`EV4-Project-Gate` is the Python transition engine for EV4 stage handoffs.

```text
EV4 stage output
        ↓
Project Gate validates evidence
        ↓
Project Gate runs deterministic transition
        ↓
Next stage receives JSON input package
```

The repository is no longer a shared-contract promotion office. It owns Project Gate package mechanics: Stage Evidence bundles, deterministic transition definitions, validation results, provenance, canonical JSON, SHA-256 tracking, diagnostics, and simple Persian reporting.

## Current implementation

```yaml
repository_role: stage_evidence_protocol_owner_and_transition_engine
primary_runtime: python
python_package: ev4_transition
cli: ev4-transition
node_runtime: auxiliary_only
ui: not_implemented
```

Implemented transition definitions:

- `architect-to-ce.v1`
- `ce-to-builder.v1`
- `builder-to-responsive.v1`

## Upload → check → download

```text
1. Upload a stage evidence bundle.
2. Run validation and a deterministic transition.
3. Download the next-stage JSON package, or receive structured diagnostics.
```

## `insufficient_evidence`

`insufficient_evidence` is a first-class status. It means the bundle is parseable, but the evidence is not enough for a safe transition. The engine does not invent missing evidence, silently fill important fields, or guess repair ownership.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

## CLI

```bash
ev4-transition validate fixtures/valid/architect-stage-bundle.v1.json
ev4-transition transition fixtures/valid/architect-stage-bundle.v1.json --transition-id architect-to-ce.v1 --output /tmp/ce-input.json
ev4-transition validate fixtures/invalid/insufficient-evidence.v1.json --format persian
ev4-transition inspect transitions
```

## Tests

```bash
pytest
```

## Boundary

This repository owns Project Gate envelope schemas, transition-result schemas, transition definitions, canonical JSON, SHA-256 provenance, diagnostics, and CLI behavior. It does not replace specialist repository domain schemas or validators.
